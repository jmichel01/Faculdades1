import logging

class BaseRepository:
    """
    Base class for enterprise data access repositories.
    Initializes logger and enforces standardized interfaces.
    """
    def __init__(self, logger_name: str) -> None:
        self.logger = logging.getLogger(logger_name)
