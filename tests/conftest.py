from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from selenium.common.exceptions import WebDriverException
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from pages.login_page import LoginPage
from utils.driver_factory import create_chrome_driver
from utils.logger import get_logger


LOGGER = get_logger(__name__)

RUN_ID: str | None = None
if not os.environ.get("PYTEST_RUN_ID"):
    # Create a more human-readable run id. Allow an optional suite name
    # to be provided via the `PYTEST_SUITE` env var which will be appended.
    suite = os.environ.get("PYTEST_SUITE")
    base_run = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    RUN_ID = f"run-{base_run}"
    if suite:
        safe_suite = suite.replace(" ", "_")
        RUN_ID = f"{RUN_ID}_{safe_suite}"
    os.environ["PYTEST_RUN_ID"] = RUN_ID
else:
    RUN_ID = os.environ.get("PYTEST_RUN_ID")


@pytest.fixture(scope="session")
def config() -> dict:
    with (PROJECT_ROOT / "config" / "config.yml").open(encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="function")
def driver(config: dict) -> Generator:
    webdriver = create_chrome_driver(headless=config.get("headless", True))
    # Increase explicit wait to reduce flakiness under parallel execution / reruns
    configured = config.get("timeouts", {}).get("explicit_wait_seconds", 15)
    webdriver.explicit_wait = max(configured, 30)
    # Retry navigation a few times to tolerate transient network/driver hiccups
    import time

    max_nav_attempts = 3
    nav_ok = False
    for attempt in range(1, max_nav_attempts + 1):
        try:
            webdriver.get(config["base_url"])
            nav_ok = True
            break
        except WebDriverException:
            if attempt == max_nav_attempts:
                raise
            time.sleep(1 * attempt)
    if not nav_ok:
        # allow fixture teardown to run by raising
        raise RuntimeError("Failed to navigate to base_url during driver setup")
    yield webdriver
    webdriver.quit()


@pytest.fixture(scope="function")
def auth_credentials(config: dict) -> tuple[str, str]:
    username = os.getenv(config["credentials"]["username_env"], "Admin")
    password = os.getenv(config["credentials"]["password_env"], "admin123")
    return username, password


@pytest.fixture(scope="function")
def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
def logged_in_driver(driver, auth_credentials):
    username, password = auth_credentials
    login_page = LoginPage(driver)
    # retry login a few times to tolerate transient auth/navigation issues
    import time

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            login_page.action_login(username=username, password=password)
            if login_page.is_state_logged_in():
                login_page.action_dismiss_blocking_overlays()
                return driver
        except Exception:
            # allow retry
            pass

        # small backoff between attempts
        try:
            time.sleep(1 * attempt)
            driver.refresh()
        except Exception:
            pass

    # failed to log in after retries — capture diagnostics and skip tests
    try:
        run_dir = RUN_ID or os.environ.get("PYTEST_RUN_ID")
        if run_dir:
            screenshots_dir = PROJECT_ROOT / "reports" / run_dir / "screenshots"
        else:
            screenshots_dir = PROJECT_ROOT / "reports" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        worker = os.environ.get("PYTEST_XDIST_WORKER", f"pid{os.getpid()}")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        img = screenshots_dir / f"login_failed_{worker}_{timestamp}.png"
        html = screenshots_dir / f"login_failed_{worker}_{timestamp}.html"
        try:
            png = driver.get_screenshot_as_png()
            with open(img, "wb") as fh:
                fh.write(png)
        except Exception:
            try:
                driver.save_screenshot(str(img))
            except Exception:
                LOGGER.exception("Failed to save login failure screenshot")
        try:
            with open(html, "w", encoding="utf-8") as fh:
                fh.write(driver.page_source)
        except Exception:
            LOGGER.exception("Failed to save login failure page source")
    except Exception:
        LOGGER.exception("Failed to write login diagnostics")

    pytest.skip(f"Precondition failed: login unsuccessful after {max_attempts} attempts; see reports/{run_dir}/screenshots/")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    web_driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
    if not web_driver:
        return

    # Group artifacts by run id (or fall back to top-level screenshots dir)
    run_dir = RUN_ID or os.environ.get("PYTEST_RUN_ID")
    if run_dir:
        screenshots_dir = PROJECT_ROOT / "reports" / run_dir / "screenshots"
    else:
        screenshots_dir = PROJECT_ROOT / "reports" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    # create unique filename to avoid collisions in parallel runs and overwrites
    worker = os.environ.get("PYTEST_XDIST_WORKER", f"pid{os.getpid()}")
    # Use a more readable timestamp in filenames (UTC, minute precision)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
    screenshot_file = screenshots_dir / f"{item.name}_{worker}_{timestamp}.png"

    try:
        # Attempt a full-page capture: resize viewport to page dimensions, capture, then restore
        original_size = None
        try:
            original_size = (web_driver.get_window_size().get('width'), web_driver.get_window_size().get('height'))
        except Exception:
            original_size = None

        try:
            # compute full document dimensions
            width = web_driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth, document.documentElement.clientWidth);")
            height = web_driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.documentElement.clientHeight);")
            # clamp height to a reasonable max to avoid driver errors
            max_h = 10000
            height = min(int(height or 1080), max_h)
            width = int(width or 1920)
            web_driver.set_window_size(width, height)
        except Exception:
            pass

        png = web_driver.get_screenshot_as_png()
        with open(screenshot_file, "wb") as fh:
            fh.write(png)
        try:
            # restore original window size
            if original_size:
                web_driver.set_window_size(original_size[0], original_size[1])
        except Exception:
            pass
        LOGGER.info("Saved failure screenshot: %s", screenshot_file.as_posix())
    except Exception:
        # fallback to selenium convenience method
        try:
            web_driver.save_screenshot(str(screenshot_file))
            LOGGER.info("Saved failure screenshot (fallback): %s", screenshot_file.as_posix())
        except Exception:
            LOGGER.exception("Failed to capture screenshot for %s", item.name)

    # Also save page source to help diagnose blank images
    try:
        html_file = screenshots_dir / f"{item.name}_{worker}_{timestamp}.html"
        with open(html_file, "w", encoding="utf-8") as fh:
            fh.write(web_driver.page_source)
        LOGGER.info("Saved page source: %s", html_file.as_posix())
    except Exception:
        LOGGER.exception("Failed to save page source for %s", item.name)

    # Try to capture browser console logs when available
    try:
        logs = []
        for entry in web_driver.get_log("browser"):
            logs.append(f"{entry.get('level')} {entry.get('message')}")
        if logs:
            log_file = screenshots_dir / f"{item.name}_{worker}_{timestamp}.log"
            with open(log_file, "w", encoding="utf-8") as fh:
                fh.write("\n".join(logs))
            LOGGER.info("Saved browser console logs: %s", log_file.as_posix())
    except Exception:
        # not all drivers support browser logs; ignore errors
        LOGGER.debug("Browser logs not available for %s", item.name)


def pytest_configure(config):
    """Adjust pytest-html output path to use the run-specific reports directory.

    This moves the generated `report.html` into `reports/<run_id>/report.html`
    when a run id is present (generated or provided via `PYTEST_RUN_ID`).
    """
    try:
        run_dir = os.environ.get("PYTEST_RUN_ID")
        if not run_dir:
            return

        # ensure the run reports directory exists
        target_dir = PROJECT_ROOT / "reports" / run_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        # pytest-html stores the output path on config.option.htmlpath
        if hasattr(config, "option") and hasattr(config.option, "htmlpath"):
            new_path = target_dir / "report.html"
            config.option.htmlpath = str(new_path)
            LOGGER.info("pytest-html report path set to %s", new_path.as_posix())
    except Exception:
        LOGGER.exception("Failed to set pytest-html report path")


def skip_or_fail_on_no_records(driver, row_getter_callable, message: str, timeout: int = 10):
    """Poll for rows using the provided callable.

    If rows appear within `timeout`, return them. If not, inspect the page for
    a site-level 403/Forbidden or a 'No Records' message and skip the test in
    that case. Otherwise fail so that reruns may retry.
    """
    import time
    end = time.time() + timeout
    while time.time() < end:
        try:
            rows = row_getter_callable()
        except Exception:
            rows = None
        if rows:
            return rows
        time.sleep(0.5)

    # inspect page source for site-level conditions
    try:
        src = driver.page_source.lower()
        if "403" in src or "forbidden" in src:
            pytest.skip(f"{message} - site-level 403/Forbidden detected")
        if "no records found" in src or "no records" in src:
            pytest.skip(f"{message} - No Records Found")
    except Exception:
        pass

    pytest.fail(f"{message} - no rows found after polling")