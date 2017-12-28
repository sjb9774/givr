import logging, sys

def get_logger(name):
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - (%(funcName)s): %(message)s")
    ch.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(ch)
    return logger