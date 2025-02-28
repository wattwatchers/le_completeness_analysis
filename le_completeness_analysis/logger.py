import logging
from config import AppConfig


def get_logger(config: AppConfig) -> logging.Logger:
    logger = logging.getLogger("rayve_qa")
    logger.setLevel(config.LOGGING_LEVEL)

    # loggers are cached, so if we call this from multiple places we end up with multiple handlers
    if logger.hasHandlers():
        return logger

    stdout_handler = logging.StreamHandler()
    formatter: logging.Formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    return logger
