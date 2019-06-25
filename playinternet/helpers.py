import logging
from logging.handlers import RotatingFileHandler
from os import path
from os import makedirs
import sys


def set_logger(logger, filename, level):
    script_dir = path.dirname(path.realpath(sys.argv[0]))
    if not path.exists(path.join(script_dir, 'log')):
        makedirs(path.join(script_dir, 'log'))

    handler = RotatingFileHandler(path.join(script_dir, 'log', filename), maxBytes=1048576,
                                  backupCount=3)

    formatter = logging.Formatter(
        '%(asctime)s%(levelname)8s()|%(filename)s:%(lineno)s - %(funcName)s() - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
