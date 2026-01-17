import sys
import os
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler

from src.config.settings import settings


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(settings.log_level)

    current_dir = Path(__file__).resolve().parent

    log_dir = current_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_filename = Path(settings.log_file).name
    full_log_path = log_dir / log_filename


    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    fh = RotatingFileHandler(
        full_log_path,   
        maxBytes=10485760,
        backupCount=5
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger