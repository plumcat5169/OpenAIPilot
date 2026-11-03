"""
Logging configuration for OpenAIPilot.
Creates a logger named "OpenAIPilot" that logs to console and to a rotating file under the `logs` directory.
"""

import logging
import os
from .config import load_config


def setup_logger():
    cfg = load_config()
    level_name = cfg.get("log_level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger("OpenAIPilot")
    logger.setLevel(level)

    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (rotating)
    fh = logging.FileHandler("logs/openai_pilot.log", encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

# Export a module‑level logger for convenient imports
logger = setup_logger()
