import time
from helpers.log import Log

class Time:
    @staticmethod
    def get_unix() -> float:
        return time.time()

    @staticmethod
    def get_hours_between_ms(start_unix: float, end_unix: float) -> float:
        return end_unix - start_unix