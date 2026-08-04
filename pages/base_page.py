from __future__ import annotations

"""Shared page object base helpers used across page classes."""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from utils.wait_helpers import wait_clickable, wait_invisible, wait_present, wait_visible


class BasePage:
    """Reusable page methods with explicit waits and stale retry handling."""

    LOC_DROPDOWN_OPTIONS = (By.CSS_SELECTOR, ".oxd-dropdown-option")
    LOC_REQUIRED_ERRORS = (By.CSS_SELECTOR, ".oxd-input-field-error-message")
    LOC_PAGE_HEADER = (By.CSS_SELECTOR, ".oxd-topbar-header-breadcrumb h6")
    LOC_OVERLAY = (By.CSS_SELECTOR, ".oxd-overlay, .oxd-layout-overlay")
    LOC_DIALOG_CLOSE = (By.CSS_SELECTOR, ".oxd-dialog-close-button")
    LOC_SIDEBAR_TOGGLE = (By.XPATH, "//i[contains(@class,'oxd-topbar-header-hamburger')]/ancestor::button[1]",)
    LOC_MENU_ITEM = (By.XPATH, "//a[contains(@class,'oxd-main-menu-item')]//span",)

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = getattr(driver, "explicit_wait", timeout)

    def open(self, url: str) -> None:
        self.driver.get(url)

    def action_click(self, by: By, locator: str) -> None:
        # Click an element with a small retry loop and JS fallback for stubborn elements
        for _ in range(2):
            try:
                wait_clickable(self.driver, by, locator, self.timeout).click()
                return
            except StaleElementReferenceException:
                continue
            except (ElementClickInterceptedException, ElementNotInteractableException, TimeoutException):
                break

        element = wait_present(self.driver, by, locator, self.timeout)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
            element,
        )

    def action_type(self, by: By, locator: str, value: str) -> None:
        # Type into a visible input element
        element = wait_visible(self.driver, by, locator, self.timeout)
        element.clear()
        element.send_keys(value)

    def action_clear_and_type(self, by: By, locator: str, value: str) -> None:
        # Clear an element and type, preferring clickable then visible
        try:
            element = wait_clickable(self.driver, by, locator, self.timeout)
        except TimeoutException:
            element = wait_visible(self.driver, by, locator, self.timeout)

        element.clear()
        element.send_keys(value)

    def get_text(self, by: By, locator: str) -> str:
        # Return stripped visible text of an element
        return wait_visible(self.driver, by, locator, self.timeout).text.strip()

    def is_visible(self, by: By, locator: str) -> bool:
        try:
            # Wait until the element is visible
            wait_visible(self.driver, by, locator, self.timeout)
            return True
        except Exception:
            return False

    def get_element_count(self, by: By, locator: str) -> int:
        # Return count of present elements matching locator
        wait_present(self.driver, by, locator, self.timeout)
        return len(self.driver.find_elements(by, locator))

    def get_required_error_count(self) -> int:
        return len(self.driver.find_elements(*self.LOC_REQUIRED_ERRORS))

    def get_required_error_messages(self) -> list[str]:
        return [
            element.text.strip()
            for element in self.driver.find_elements(*self.LOC_REQUIRED_ERRORS)
            if element.text.strip()
        ]

    def is_text_visible(self, text: str) -> bool:
        locator = (
            By.XPATH,
            f"//*[contains(normalize-space(),'{text}')]",
        )
        return self.is_visible(*locator)

    def is_present(self, by: By, locator: str) -> bool:
        """Return True if element(s) matching locator are present in the DOM without waiting."""
        try:
            return len(self.driver.find_elements(by, locator)) > 0
        except Exception:
            return False

    def action_select_dropdown_by_label(self, label: str, option_text: str) -> None:
        # Select an option from a labeled dropdown by visible option text
        dropdown = (
            By.XPATH,
            f"//label[normalize-space()='{label}']"
            f"/../following-sibling::div//div[contains(@class,'oxd-select-text')]",
        )
        self.action_click(*dropdown)
        option = (
            By.XPATH,
            f"//div[@role='listbox']//span[normalize-space()='{option_text}']",
        )
        self.action_click(*option)

    def action_click_button(self, label: str) -> None:
        # Click a button by its visible label
        locator = (By.XPATH, f"//button[normalize-space()='{label}']")
        self.action_click(*locator)

    def get_page_header(self) -> str:
        # Return the page header text
        return self.get_text(*self.LOC_PAGE_HEADER)

    def action_dismiss_blocking_overlays(self) -> None:
        # Try dismissing modals/overlays that block interaction
        for _ in range(3):
            close_buttons = self.driver.find_elements(*self.LOC_DIALOG_CLOSE)
            clicked = False
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    clicked = True
                    break
            if clicked:
                try:
                    wait_invisible(self.driver, *self.LOC_OVERLAY, 3)
                except Exception:
                    pass
                continue

            overlays = [
                overlay
                for overlay in self.driver.find_elements(*self.LOC_OVERLAY)
                if overlay.is_displayed()
            ]
            if not overlays:
                return

            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    def action_ensure_sidebar_expanded(self) -> None:
        # Ensure the side menu is expanded so menu items are visible
        visible_items = [
            item
            for item in self.driver.find_elements(*self.LOC_MENU_ITEM)
            if item.is_displayed()
        ]
        if visible_items:
            return

        try:
            toggle = wait_clickable(self.driver, *self.LOC_SIDEBAR_TOGGLE, 5)
            toggle.click()
        except Exception:
            pass

    def action_js_click(self, by: By, locator: str) -> None:
        # Click using JavaScript when standard click fails
        element = wait_present(self.driver, by, locator, self.timeout)
        self.driver.execute_script("arguments[0].click();", element)

    def ensure_section_expanded(self, section_label: str) -> None:
        """If a collapsible section with the given label exists, ensure it's expanded.

        Looks for a nearby toggle button and clicks it if the section appears collapsed.
        """
        # Expand a collapsible section if a toggle exists
        try:
            toggle = self.driver.find_element(By.XPATH, f"//div[contains(. ,'{section_label}')]//button")
            if toggle and toggle.is_displayed():
                try:
                    toggle.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", toggle)
        except Exception:
            # No section toggle found; ignore
            pass