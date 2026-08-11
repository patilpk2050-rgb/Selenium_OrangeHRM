from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.wait_helpers import wait_visible


class MaintenancePage(BasePage):
    LOC_PASSWORD_MODAL = (
        By.XPATH,
        "//div[contains(@class,'oxd-dialog-container') or contains(.,'Admin Access') or //label[contains(normalize-space(),'Password')]]",
    )
    LOC_PASSWORD_INPUT = (By.XPATH, "//input[@type='password' or contains(@placeholder,'Password')]")
    LOC_PASSWORD_CONFIRM = (By.XPATH, "//button[normalize-space()='Confirm'] | //button[normalize-space()='Submit'] | //button[contains(.,'Confirm')]")
    LOC_INVALID_CREDENTIALS = (By.XPATH, "//*[contains(normalize-space(),'Invalid') or contains(normalize-space(),'invalid') or contains(.,'Invalid credentials')]")

    LOC_MAINTENANCE_HEADER = (
        By.XPATH,
        "//h6[contains(normalize-space(),'Purge Employee Records') or contains(normalize-space(),'Maintenance') or contains(normalize-space(),'Purge')]")


    def is_password_prompt_visible(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_PASSWORD_MODAL, 5)
            return True
        except Exception:
            return False

    def submit_password(self, password: str) -> None:
        # Enter the admin password prompt and confirm to gain access
        try:
            self.action_clear_and_type(*self.LOC_PASSWORD_INPUT, password)
        except Exception:
            try:
                el = self.driver.find_element(*self.LOC_PASSWORD_INPUT)
                self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", el, password)
            except Exception:
                pass
        try:
            self.action_click(*self.LOC_PASSWORD_CONFIRM)
        except Exception:
            pass

    def is_maintenance_landing_visible(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_MAINTENANCE_HEADER, self.timeout)
            return True
        except Exception:
            return False

    def is_invalid_credentials_visible(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_INVALID_CREDENTIALS, 3)
            return True
        except Exception:
            return False