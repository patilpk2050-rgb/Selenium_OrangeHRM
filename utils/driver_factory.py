from __future__ import annotations

import os
import time 
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

"""Factory for creating configured Chrome WebDriver instances used in tests."""

def _clear_stale_wdm_lock(max_age_seconds: int = 120) -> None: 
    """Remove stale webdriver-manager lock files that block driver setup on Windows."""
    lock_dir = Path.home() / ".wdm"
    if not lock_dir.exists():
        return

    now = time.time()
    for lock_file in lock_dir.glob(".wdm-lock-*"):
        try:
            file_age = now - lock_file.stat().st_mtime
            if file_age > max_age_seconds:
                lock_file.unlink(missing_ok=True)
        except OSError:
            continue
            
            
def create_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    # Ensure consistent device scale and DPI handling across Windows environments
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--high-dpi-support=1")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    _clear_stale_wdm_lock()

    last_exc: Exception | None = None
    for _ in range(3):
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.maximize_window()
            return driver
        except Exception as exc:
            last_exc = exc

    os.environ.setdefault("SE_MANAGER_DRIVER_TIMEOUT", "120")
    try:
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver
    except Exception:
        if last_exc:
            raise last_exc
        raise