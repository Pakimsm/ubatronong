import logging
from datetime import datetime
from pathlib import Path


def setup_logger(
    module_name: str,
    log_dir: Path = Path("data/logs"),
) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{module_name}_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(module_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s — %(message)s", "%H:%M:%S"
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
