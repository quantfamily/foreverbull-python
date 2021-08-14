import logging

from foreverbull.foreverbull import Foreverbull
from foreverbull.worker import Worker

loggers = {}


def get_logger(name):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    logger.addHandler(handler)
    loggers[name] = logger
    return logger


__all__ = [Foreverbull, Worker]
