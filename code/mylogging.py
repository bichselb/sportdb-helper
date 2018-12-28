import logging
from logging.handlers import RotatingFileHandler
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, 'logs')
log_file = os.path.join(log_path, 'logs.log')


def create_logger():
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')

    # add a rotating handler
    handler = RotatingFileHandler(log_file, backupCount=50)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # force rollover if files exists
    if os.path.isfile(log_file):
        handler.doRollover()

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = create_logger()

