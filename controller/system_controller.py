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
        """Open an application using the Windows Start menu search (Win+S)."""
        logger.info(f"Opening '{app_name}' via Windows Search")
        # Press Win+S to focus the search bar (Win alone also works but Win+S is explicit)
        pyautogui.hotkey('win', 's')
        time.sleep(0.5)
        pyautogui.typewrite(app_name, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        logger.debug(f"Sent keystrokes to start {app_name}")

    # ---------------------------------------------------------------------
    # High‑level orchestration
    # ---------------------------------------------------------------------
    def ensure_running(self, app_name: str, exe_name: str):
        """Make sure *app_name* is running.

        - Checks if a process with *exe_name* is already active.
        - If not, tries to locate the executable on disk and launch it.
        - If the executable cannot be located, falls back to opening the app via the Start menu.
        """
        if self.is_process_running(exe_name):
            logger.info(f"{app_name} is already running.")
            return

        logger.info(f"{app_name} is not running – attempting to start it.")
        exe_path = self.find_executable(exe_name)
        if exe_path:
            self.launch_application(exe_path)
        else:
            self.open_via_start_menu(app_name)
