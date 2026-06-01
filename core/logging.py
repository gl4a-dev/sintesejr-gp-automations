import logging

from core.settings import LOG_FILE, LOG_LEVEL


def configure_logging(level:int = LOG_LEVEL, save_to_file:bool = False):
    handlers = [logging.StreamHandler()]

    if save_to_file:
        handlers.append(logging.FileHandler(LOG_FILE))

    logging.basicConfig(
        level=level,
        format=(
            "[%(asctime)s] "
            "[%(levelname)s] "
            "[%(name)s] "
            "%(message)s"
        ),
        handlers=handlers
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)