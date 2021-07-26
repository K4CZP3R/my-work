import time


class TimeHelpers:
    @staticmethod
    def get_unix() -> float:
        return time.time()