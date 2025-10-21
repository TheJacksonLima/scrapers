import logging
from logging.handlers import RotatingFileHandler
from car_scraper.utils.config import settings

def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s.%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = RotatingFileHandler(settings.LOG_FILE, maxBytes=5_000_000, backupCount=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.propagate = False

    return logger
