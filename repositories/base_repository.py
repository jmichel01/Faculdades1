import logging

class BaseRepository:
    def __init__(self, logger_name: str) -> None:
        self.logger = logging.getLogger(logger_name)
#A
