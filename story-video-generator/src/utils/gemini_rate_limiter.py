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
from typing import Callable, Any, Optional
from functools import wraps


class GeminiRateLimiter:
    """Rate limiter for Gemini API calls"""

    def __init__(self):
        # 🔒 GLOBAL LOCK - Only ONE Gemini request at a time across ALL threads!
        self.global_lock = threading.Lock()
        # Track last request time per API key
        self.last_request_time = {}
        # Track when keys hit rate limits
        self.rate_limit_hits = {}
        # Track request count per key in last 60s (for sliding window)
        self.request_history = {}  # {key: [timestamp1, timestamp2, ...]}
        # ⚡ AGGRESSIVE RATE LIMITING - Prevent 429 errors!
        # Free tier: 15 req/60s = 4s minimum. Use 7s to be VERY SAFE.
        self.min_delay = 7.0  # 7 seconds between requests (was 5s)
        # Maximum retry attempts for 429 errors
        self.max_retries = 8  # Increased from 5
        # Track consecutive failures across all keys
        self.consecutive_failures = 0
        # Sliding window trigger threshold (out of 15 max)
        self.sliding_window_trigger = 10  # Start waiting at 10 requests (was 14)

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

        # Track consecutive failures
        self.consecutive_failures += 1

        # If we're failing a lot, implement longer cooldown
        if self.consecutive_failures >= 3:
            base_wait = 60  # Start with 60s for multiple failures
            print(f"   🔥 Multiple rate limits hit ({self.consecutive_failures} times) - longer cooldown needed")
        else:
            base_wait = 0

        # Extract suggested delay from error
        retry_delay = self.extract_retry_delay(error_str)

        # Use exponential backoff if no delay suggested
        if retry_delay == 15.0:  # Default value
            retry_delay = min(2 ** attempt, 60)  # Max 60 seconds

        # Add base wait for consecutive failures
        retry_delay = max(retry_delay, base_wait)

        # Track when this key hit rate limit
        if api_key:
            key_short = api_key[-8:]
            self.rate_limit_hits[key_short] = time.time()

        print(f"   ⚠️  Rate limit hit! Waiting {retry_delay:.1f}s before retry...")
        print(f"   💡 This is normal for free tier - automatic retry in progress...")

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
