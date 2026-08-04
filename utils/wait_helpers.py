from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

"""Small wrappers around Selenium expected conditions for consistent waits."""


def wait_visible(driver: WebDriver, by: By, locator: str, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(
        ec.visibility_of_element_located((by, locator))
    )


def wait_clickable(driver: WebDriver, by: By, locator: str, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(
        ec.element_to_be_clickable((by, locator))
    )


def wait_present(driver: WebDriver, by: By, locator: str, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(
        ec.presence_of_element_located((by, locator))
    )


def wait_url_contains(driver: WebDriver, text: str, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(ec.url_contains(text))


def wait_invisible(driver: WebDriver, by: By, locator: str, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(
        ec.invisibility_of_element_located((by, locator))
    )