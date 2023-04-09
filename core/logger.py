import logging
from datetime import datetime


def log(name):
    file_name = f"{str(datetime.today()).split(' ')[0]}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(f"logs/{file_name}", mode='w', encoding='utf-8')
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
