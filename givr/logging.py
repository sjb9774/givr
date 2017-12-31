import logging, sys, os

def get_logger(name):
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join("logs", "debug.log"))
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - (%(funcName)s): %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
