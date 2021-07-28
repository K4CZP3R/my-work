from helpers.singleton import Singleton
import logging


class Log(metaclass=Singleton):
    def __init__(self) -> None:
        self.logger = logging.getLogger("ksp-logger")
    
    def info(self, msg): 
        self.logger.info(msg)
    def error(self, msg):
        self.logger.error(msg)