import logging
from pathlib import Path


def setup_logger():
    log_dir = Path.home() / "AppData" / "Local" / "WinClean" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "winclean.log"

    logger = logging.getLogger("WinClean")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
