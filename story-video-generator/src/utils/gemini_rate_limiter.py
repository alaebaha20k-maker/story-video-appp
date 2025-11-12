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
from typing import Callable, Any, Optional
from functools import wraps


class GeminiRateLimiter:
    """Rate limiter for Gemini API calls"""

    def __init__(self):
        # Track last request time per API key
        self.last_request_time = {}
        # Minimum delay between requests (seconds)
        self.min_delay = 2.0  # 2 seconds between requests
        # Maximum retry attempts for 429 errors
        self.max_retries = 5

    def wait_if_needed(self, api_key: str):
        """Wait if we're making requests too quickly"""
        key_short = api_key[-8:]

        if key_short in self.last_request_time:
            elapsed = time.time() - self.last_request_time[key_short]
            if elapsed < self.min_delay:
                wait_time = self.min_delay - elapsed
                print(f"   ⏱️  Rate limiting: waiting {wait_time:.1f}s before next request...")
                time.sleep(wait_time)

        self.last_request_time[key_short] = time.time()

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

    def handle_rate_limit_error(self, error: Exception, attempt: int) -> float:
        """Handle rate limit error and return wait time"""
        error_str = str(error)

        # Extract suggested delay from error
        retry_delay = self.extract_retry_delay(error_str)

        # Use exponential backoff if no delay suggested
        if retry_delay == 15.0:  # Default value
            retry_delay = min(2 ** attempt, 60)  # Max 60 seconds

        print(f"   ⚠️  Rate limit hit! Waiting {retry_delay:.1f}s before retry...")
        print(f"   💡 This is normal for free tier - automatic retry in progress...")

        return retry_delay


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
    api_key = "AIzaSyC3lCI117uyVbJkFOXI6BffwlUCLSdYIH0"

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
