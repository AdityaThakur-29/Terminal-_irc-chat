"""
Rate limiting to prevent message flooding
"""

import time
import threading
from collections import defaultdict, deque


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, max_messages=30, time_window=60):
        """
        Args:
            max_messages: Maximum messages allowed in time window
            time_window: Time window in seconds
        """
        self.max_messages = max_messages
        self.time_window = time_window
        self.user_messages = defaultdict(deque)
        self.lock = threading.Lock()

    def is_allowed(self, nickname):
        """
        Check if user is allowed to send message
        Returns: True if allowed, False if rate limited
        """
        with self.lock:
            now = time.time()

            # Get user's message history
            messages = self.user_messages[nickname]

            # Remove old messages outside time window
            while messages and messages[0] < now - self.time_window:
                messages.popleft()

            # Check if limit exceeded
            if len(messages) >= self.max_messages:
                return False

            # Add current message
            messages.append(now)
            return True

    def get_wait_time(self, nickname):
        """Get how long user must wait before next message"""
        with self.lock:
            if not self.user_messages[nickname]:
                return 0

            oldest = self.user_messages[nickname][0]
            wait = self.time_window - (time.time() - oldest)
            return max(0, int(wait))

    def reset_user(self, nickname):
        """Reset rate limit for user"""
        with self.lock:
            if nickname in self.user_messages:
                del self.user_messages[nickname]