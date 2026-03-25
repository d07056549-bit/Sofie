import logging
from logging import StreamHandler, Formatter

def setup_logging(level=logging.INFO):
    logger = logging.getLogger("global_trends")
    logger.setLevel(level)
    if not logger.handlers:
        handler = StreamHandler()
        handler.setFormatter(Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        logger.addHandler(handler)
    return logger
