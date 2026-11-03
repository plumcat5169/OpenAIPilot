"""
System controller utilities – process checking, executable discovery, and UI automation.
"""

import os
import subprocess
import time
from pathlib import Path
import psutil
import pyautogui
from ..config import load_config
from ..logger import logger
import json
import winreg



class SystemController:
    def __init__(self):
        cfg = load_config()
        # List of directories to scan for executables (expanded already by config loader)
        self.search_paths = cfg.get("app_search_paths", [])

    # ---------------------------------------------------------------------
    # Process utilities
    # ---------------------------------------------------------------------
    def is_process_running(self, process_name: str) -> bool:
        """Return True if a process with the given executable name is currently running."""
        logger.debug(f"Checking if process '{process_name}' is running...")
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                name = proc.info.get('name')
                exe = proc.info.get('exe')
                if name and name.lower() == process_name.lower():
                    logger.debug(f"Found running process by name: {proc.pid}")
                    return True
                if exe and os.path.basename(exe).lower() == process_name.lower():
                    logger.debug(f"Found running process by exe path: {proc.pid}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        logger.debug(f"Process '{process_name}' is not running.")
        return False

    # ---------------------------------------------------------------------
    # Executable discovery
    # ---------------------------------------------------------------------
    def find_executable(self, exe_name: str) -> str | None:
        """Search configured directories (and optionally the whole C: drive) for *exe_name*.
        Returns the absolute path if found, otherwise None.
        """
        logger.debug(f"Searching for executable '{exe_name}' in configured paths...")
        # First, scan the explicitly configured directories
        for base in self.search_paths:
            base_path = Path(base).expanduser()
            if not base_path.is_dir():
                continue
            for root, _, files in os.walk(base_path):
                if exe_name.lower() in (f.lower() for f in files):
                    candidate = os.path.join(root, exe_name)
                    logger.info(f"Found '{exe_name}' at {candidate}")
                    return candidate

        # Fallback: exhaustive scan of the C: drive (slow but thorough)
        logger.debug("Falling back to full C: drive scan – this may take a while.")
        for root, _, files in os.walk("C:\\"):
            if exe_name.lower() in (f.lower() for f in files):
                candidate = os.path.join(root, exe_name)
                logger.info(f"Found '{exe_name}' at {candidate} (full scan)")
                return candidate
        logger.warning(f"Executable '{exe_name}' not found after full scan.")
        return None

    # ---------------------------------------------------------------------
    # Application launch helpers
    # ---------------------------------------------------------------------
    def launch_application(self, exe_path: str):
        """Launch an application given its absolute executable path."""
        try:
            logger.info(f"Launching application: {exe_path}")
            # Using shell=True on Windows simplifies launching .exe files
            subprocess.Popen([exe_path], shell=True)
        except Exception as e:
            logger.error(f"Failed to launch {exe_path}: {e}")

    def open_via_start_menu(self, app_name: str):
        """Open an application using the Windows Start command (more reliable than UI automation)."""
        logger.info(f"Opening '{app_name}' via Windows 'start' command")
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
        except Exception as e:
            logger.error(f"Failed to start {app_name}: {e}")

    # ---------------------------------------------------------------------
    # High‑level orchestration
    # ---------------------------------------------------------------------
    def ensure_running(self, app_name: str, exe_name: str):
        """Make sure *app_name* is running.

        A quick path: if the process is already active, do nothing.
        Otherwise we immediately use the Windows Start menu search (Win+S)
        to avoid any lengthy file‑system scanning.
        """
        if self.is_process_running(exe_name):
            logger.info(f"{app_name} is already running.")
            return

        logger.info(f"{app_name} is not running – opening via Windows Search now.")
        self.open_via_start_menu(app_name)
