import time
import os
from pathlib import Path
from src.config import get_settings

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN
        self.last_state_change = time.time()

    @property
    def is_open(self) -> bool:
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if time.time() - self.last_state_change > self.recovery_timeout:
                self.state = "CLOSED"
                self.failure_count = 0
                return False
            return True
        return False

    def record_failure(self, error: str):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

def is_killed() -> bool:
    return get_settings().is_killed

# Singleton instance
circuit_breaker = CircuitBreaker()
