"""
Configuration loader for OpenAIPilot.
Loads the JSON configuration file located at the repository root.
"""

import json
import os
from pathlib import Path

# Path to the config file (repo root / config.json)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"


def load_config():
    """Load and return the configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Expand environment variables in paths (e.g., %USERNAME%)
    if "app_search_paths" in cfg:
        expanded = []
        for p in cfg["app_search_paths"]:
            expanded.append(os.path.expandvars(p))
        cfg["app_search_paths"] = expanded
    return cfg
