import random
import time


class BlinkTimer:
    def __init__(self, min_interval: float, max_interval: float, duration: float) -> None:
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.duration = duration
        self.next_blink = time.monotonic() + random.uniform(self.min_interval, self.max_interval)
        self.blink_until = 0.0

    def is_blinking(self) -> bool:
        now = time.monotonic()
        if now >= self.next_blink:
            self.blink_until = now + self.duration
            self.next_blink = now + random.uniform(self.min_interval, self.max_interval)
        return now < self.blink_until