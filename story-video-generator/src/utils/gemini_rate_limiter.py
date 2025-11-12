"""
🚦 GEMINI RATE LIMITER - Handles API rate limits and quota errors

Implements:
- Automatic retry with exponential backoff
- 429 error handling with suggested retry delays
- Rate limiting between requests
- Smart key rotation to avoid quota exhaustion
"""

import time
import re
import threading
import json
import os
from pathlib import Path
from typing import Callable, Any, Optional
from functools import wraps


class GeminiRateLimiter:
    """Rate limiter for Gemini API calls with persistent tracking"""

    def __init__(self):
        # 🔒 GLOBAL LOCK - Only ONE Gemini request at a time across ALL threads!
        self.global_lock = threading.Lock()

        # 💾 PERSISTENT STORAGE - Save request history to file
        self.history_file = Path(__file__).parent.parent.parent / "gemini_rate_history.json"

        # Track last request time per API key
        self.last_request_time = {}
        # Track when keys hit rate limits
        self.rate_limit_hits = {}
        # Track request count per key in last 60s (for sliding window)
        self.request_history = {}  # {key: [timestamp1, timestamp2, ...]}

        # ⚡ AGGRESSIVE RATE LIMITING - Prevent 429 errors!
        # Free tier: 15 req/60s = 4s minimum. Use 7s to be VERY SAFE.
        self.min_delay = 7.0  # 7 seconds between requests (was 5s)
        # Maximum retry attempts for 429 errors (REDUCED per best practices)
        self.max_retries = 2  # Only 1 retry after initial attempt (was 8)
        # Track consecutive failures across all keys
        self.consecutive_failures = 0
        # Sliding window trigger threshold (out of 15 max)
        self.sliding_window_trigger = 10  # Start waiting at 10 requests (was 14)

        # 🔄 Load persistent history on startup
        self._load_history()

        print(f"📊 Rate Limiter initialized with persistent tracking")
        self._print_current_status()

    def wait_if_needed(self, api_key: str):
        """Wait if we're making requests too quickly"""
        # 🔒 CRITICAL: Acquire global lock to prevent parallel requests across threads
        with self.global_lock:
            key_short = api_key[-8:]
            current_time = time.time()

            # Clean old requests from history (older than 90s to be safe)
            if key_short in self.request_history:
                self.request_history[key_short] = [
                    t for t in self.request_history[key_short]
                    if current_time - t < 90
                ]

            # Check if this key recently hit rate limit
            if key_short in self.rate_limit_hits:
                time_since_limit = current_time - self.rate_limit_hits[key_short]
                # If key hit limit in last 90s, wait extra time (AGGRESSIVE COOLDOWN)
                if time_since_limit < 90:
                    extra_wait = 90 - time_since_limit
                    print(f"   ⏰ RATE LIMIT COOLDOWN: Key hit limit {time_since_limit:.0f}s ago - waiting {extra_wait:.1f}s more...")
                    time.sleep(extra_wait)
                    # Clear the rate limit hit after waiting
                    del self.rate_limit_hits[key_short]
                    # Clear request history for this key
                    if key_short in self.request_history:
                        self.request_history[key_short] = []

            # Check sliding window: if key made too many requests in last 60s, wait
            if key_short in self.request_history:
                recent_requests = [t for t in self.request_history[key_short] if current_time - t < 60]
                if len(recent_requests) >= self.sliding_window_trigger:  # Aggressive threshold (10 of 15)
                    oldest_request = min(recent_requests)
                    wait_time = 65 - (current_time - oldest_request)  # Wait for oldest to age out (65s buffer)
                    if wait_time > 0:
                        print(f"   🚦 SLIDING WINDOW: {len(recent_requests)}/15 requests in last 60s - waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        # Clean up after waiting
                        self.request_history[key_short] = [
                            t for t in self.request_history[key_short]
                            if current_time + wait_time - t < 60
                        ]

            # Normal rate limiting (min delay between requests)
            if key_short in self.last_request_time:
                elapsed = current_time - self.last_request_time[key_short]
                if elapsed < self.min_delay:
                    wait_time = self.min_delay - elapsed
                    print(f"   ⏱️  MINIMUM DELAY: waiting {wait_time:.1f}s (7s minimum between requests)...")
                    time.sleep(wait_time)

            # Record this request
            self.last_request_time[key_short] = time.time()
            if key_short not in self.request_history:
                self.request_history[key_short] = []
            self.request_history[key_short].append(time.time())

            print(f"   ✅ Rate limiter: Request approved for key ...{key_short}")

            # 💾 Save history to disk after each request
            self._save_history()

    def _load_history(self):
        """Load request history from persistent storage"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)

                    self.request_history = data.get('request_history', {})
                    self.last_request_time = data.get('last_request_time', {})
                    self.rate_limit_hits = data.get('rate_limit_hits', {})

                    # Clean up old entries (older than 90s)
                    current_time = time.time()
                    for key in list(self.request_history.keys()):
                        self.request_history[key] = [
                            t for t in self.request_history[key]
                            if current_time - t < 90
                        ]

                    # Clean old rate limit hits
                    for key in list(self.rate_limit_hits.keys()):
                        if current_time - self.rate_limit_hits[key] > 90:
                            del self.rate_limit_hits[key]

                    print(f"   📂 Loaded request history from disk")
            else:
                print(f"   📂 No previous history found - starting fresh")
        except Exception as e:
            print(f"   ⚠️ Could not load history: {e}")
            # Continue with empty history
            self.request_history = {}
            self.last_request_time = {}
            self.rate_limit_hits = {}

    def _save_history(self):
        """Save request history to persistent storage"""
        try:
            data = {
                'request_history': self.request_history,
                'last_request_time': self.last_request_time,
                'rate_limit_hits': self.rate_limit_hits,
                'last_updated': time.time()
            }

            with open(self.history_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            # Don't fail if we can't save - just log it
            print(f"   ⚠️ Could not save history: {e}")

    def _print_current_status(self):
        """Print current API usage status"""
        current_time = time.time()

        for key_short, timestamps in self.request_history.items():
            recent = [t for t in timestamps if current_time - t < 60]
            if recent:
                print(f"   📊 Key ...{key_short}: {len(recent)}/15 requests in last 60s")

                # Show when window will clear
                if recent:
                    oldest = min(recent)
                    time_until_clear = 60 - (current_time - oldest)
                    if time_until_clear > 0:
                        print(f"      ⏰ Window clears in {time_until_clear:.0f}s")

    def extract_retry_delay(self, error_message: str) -> float:
        """Extract retry delay from error message"""
        # Try to find "retry in X.XXs" pattern
        match = re.search(r'retry in ([\d.]+)s', str(error_message))
        if match:
            return float(match.group(1))

        # Try to find seconds in retry_delay
        match = re.search(r'seconds: (\d+)', str(error_message))
        if match:
            return float(match.group(1))

        # Default: 15 seconds
        return 15.0

    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a 429 rate limit error"""
        error_str = str(error).lower()
        return (
            '429' in error_str or
            'quota exceeded' in error_str or
            'rate limit' in error_str or
            'resource exhausted' in error_str
        )

    def handle_rate_limit_error(self, error: Exception, attempt: int, api_key: str = None) -> float:
        """Handle rate limit error and return wait time"""
        error_str = str(error)

        # Track when this key hit rate limit
        if api_key:
            key_short = api_key[-8:]
            self.rate_limit_hits[key_short] = time.time()
            # 💾 Save immediately when rate limit is hit
            self._save_history()

        # Extract suggested delay from error (Gemini provides this)
        retry_delay = self.extract_retry_delay(error_str)

        # If no delay suggested, use 90s (one full sliding window)
        if retry_delay == 15.0:  # Default value means no delay found
            retry_delay = 90.0  # Wait for full sliding window to clear
            print(f"   ⚠️  Rate limit hit! No retry delay provided - waiting {retry_delay:.0f}s (full sliding window)...")
        else:
            # Use server's suggested delay
            print(f"   ⚠️  Rate limit hit! Using server's suggested delay: {retry_delay:.1f}s...")

        print(f"   💡 Attempt {attempt + 1}/{self.max_retries} - This may indicate your API key was used recently")

        return retry_delay

    def reset_failures(self):
        """Reset consecutive failure count after success"""
        self.consecutive_failures = 0

    def get_best_available_key(self, api_keys: list) -> tuple:
        """
        Select the best API key to use based on recent usage
        Returns: (best_key_index, reason)
        """
        current_time = time.time()
        best_key = 0
        best_score = -9999
        best_reason = ""

        for i, api_key in enumerate(api_keys):
            key_short = api_key[-8:]
            score = 100  # Start with perfect score

            # Penalty if key recently hit rate limit (very bad!)
            if key_short in self.rate_limit_hits:
                time_since = current_time - self.rate_limit_hits[key_short]
                if time_since < 90:  # 90s cooldown
                    score -= 1000  # Heavy penalty - don't use this key!
                    continue

            # Penalty based on requests in last 60s
            if key_short in self.request_history:
                recent = [t for t in self.request_history[key_short] if current_time - t < 60]
                requests_in_window = len(recent)
                score -= requests_in_window * 15  # More requests = worse score (increased penalty)

                if requests_in_window >= self.sliding_window_trigger:  # Use same threshold (10)
                    score -= 800  # Very bad - approaching limit!

            # Penalty based on recency
            if key_short in self.last_request_time:
                seconds_since_last = current_time - self.last_request_time[key_short]
                score += seconds_since_last  # More time = better score

            if score > best_score:
                best_score = score
                best_key = i
                best_reason = f"Score: {score:.0f}, Recent requests: {len(recent) if key_short in self.request_history and 'recent' in locals() else 0}/15"

        return (best_key, best_reason)


# Global instance
rate_limiter = GeminiRateLimiter()


def with_retry_and_rate_limit(max_attempts: int = 5):
    """
    Decorator that adds automatic retry with rate limiting

    Usage:
        @with_retry_and_rate_limit(max_attempts=5)
        def my_gemini_call(api_key):
            # ... make API call
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_attempts):
                try:
                    # Extract API key if it's in args or kwargs
                    api_key = None
                    if 'api_key' in kwargs:
                        api_key = kwargs['api_key']
                    elif len(args) > 0 and isinstance(args[0], str) and args[0].startswith('AIza'):
                        api_key = args[0]

                    # Rate limit if we have an API key
                    if api_key:
                        rate_limiter.wait_if_needed(api_key)

                    # Execute function
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e

                    # Check if it's a rate limit error
                    if rate_limiter.is_rate_limit_error(e):
                        if attempt < max_attempts - 1:
                            wait_time = rate_limiter.handle_rate_limit_error(e, attempt)
                            time.sleep(wait_time)
                            continue

                    # If not a rate limit error, or last attempt, raise
                    if attempt == max_attempts - 1:
                        raise

                    # For other errors, small delay before retry
                    time.sleep(1)

            # If all attempts failed, raise last error
            raise last_error

        return wrapper
    return decorator


if __name__ == "__main__":
    print("\n🧪 Testing Gemini Rate Limiter...\n")

    limiter = GeminiRateLimiter()

    # Test rate limiting
    print("1. Testing rate limiting (2s delay):")
    api_key = "AIzaSyAyI5VYus18_vStkISQ-ioVw3zzaQFE0qo"  # Single key for monitoring

    for i in range(3):
        print(f"\n   Request {i+1}:")
        start = time.time()
        limiter.wait_if_needed(api_key)
        elapsed = time.time() - start
        print(f"   ✅ Waited {elapsed:.2f}s")

    # Test error detection
    print("\n2. Testing rate limit error detection:")
    test_errors = [
        "429 Too Many Requests",
        "Quota exceeded for metric",
        "Please retry in 12.5s",
        "Resource exhausted"
    ]

    for error_msg in test_errors:
        is_rate_limit = limiter.is_rate_limit_error(Exception(error_msg))
        print(f"   {error_msg[:30]}: {'✅ Detected' if is_rate_limit else '❌ Not detected'}")

    # Test retry delay extraction
    print("\n3. Testing retry delay extraction:")
    error_with_delay = "Please retry in 12.166681661s"
    delay = limiter.extract_retry_delay(error_with_delay)
    print(f"   Extracted delay: {delay}s")

    print("\n✅ Rate Limiter working!\n")
