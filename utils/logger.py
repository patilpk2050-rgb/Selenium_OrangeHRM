from __future__ import annotations

import logging
from pathlib import Path

"""Simple logger factory that writes to reports/logs and stdout."""

def get_logger(name: str) -> logging.Logger:
    """Returns a timestamped INFO logger with file and console handlers"""
    logs_dir = Path("reports/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    file_handler = logging.FileHandler(logs_dir / "execution.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger