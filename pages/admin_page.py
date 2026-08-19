from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)

from pages.base_page import BasePage
from utils.wait_helpers import wait_present, wait_visible, wait_url_contains


class AdminPage(BasePage):
    LOC_SYSTEM_USERS_HEADER = (
        By.XPATH,
        "//*[normalize-space()='System Users']",
    )
    LOC_FILTER_TOGGLE = (
        By.XPATH,
        "//div[contains(@class,'oxd-table-filter-header-options')]//button[contains(@class,'oxd-icon-button')]",
    )
    LOC_USERNAME_FILTER = (
        By.XPATH,
        "//label[normalize-space()='Username']/../following-sibling::div//input | //input[@placeholder='Username' or contains(@placeholder,'Username')]",
    )
    # user role / status filters removed (requirements FR-ADM-03 & FR-ADM-04)
    LOC_SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search']")
    LOC_ADD_BUTTON = (By.XPATH, "//button[normalize-space()='Add']")
    LOC_TABLE_ROWS = (
        By.XPATH,
        "//div[contains(@class,'oxd-table-body')]//div[@role='row'] | //div[contains(@class,'oxd-table-card')]",
    )
    LOC_NO_RECORDS = (By.XPATH, "//*[normalize-space()='No Records Found']")
    LOC_ADD_USER_HEADER = (By.XPATH, "//h6[normalize-space()='Add User']")
    LOC_ADD_USER_ROLE = (
        By.XPATH,
        "//label[normalize-space()='User Role']/../following-sibling::div//div[contains(@class,'oxd-select-text')] | //div[contains(@class,'oxd-form-row')]//label[normalize-space()='User Role']/following::div[contains(@class,'oxd-select-text')][1]",
    )
    LOC_ADD_EMPLOYEE_NAME = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']/../following-sibling::div//input | //input[@placeholder='Type for hints...']",
    )
    LOC_ADD_STATUS = (
        By.XPATH,
        "//label[normalize-space()='Status']/../following-sibling::div//div[contains(@class,'oxd-select-text')] | //div[contains(@class,'oxd-form-row')]//label[normalize-space()='Status']/following::div[contains(@class,'oxd-select-text')][1]",
    )
    LOC_ADD_USERNAME = (
        By.XPATH,
        "//label[normalize-space()='Username']/../following-sibling::div//input | //input[@placeholder='Username' or @name='username']",
    )
    LOC_ADD_PASSWORD = (
        By.XPATH,
        "//label[normalize-space()='Password']/../following-sibling::div//input | //input[@type='password' and contains(@name,'password')][1]",
    )
    LOC_ADD_CONFIRM_PASSWORD = (
        By.XPATH,
        "//label[normalize-space()='Confirm Password']/../following-sibling::div//input | //input[@type='password' and contains(@name,'confirm')]",
    )

    def is_system_users_loaded(self) -> bool:
        try:
            wait_url_contains(self.driver, "/admin", self.timeout)
        except Exception:
            return False

        try:
            if self.is_visible(*self.LOC_SYSTEM_USERS_HEADER):
                return True
        except Exception:
            pass

        page_text = (self.driver.page_source or "").lower()
        if "system users" in page_text or "user management" in page_text:
            return True

        try:
            rows = self.get_table_row_texts()
            if rows:
                return True
        except Exception:
            pass

        return False

    def _find_element_resilient(self, by, locator):
        """Try visibility wait first, then fall back to presence + scroll.

        Returns the WebElement or raises the original exception.
        """
        try:
            el = wait_visible(self.driver, by, locator, self.timeout)
            if el.is_displayed() and el.is_enabled():
                return el
        except Exception:
            pass

        # fallback: look for any present matching element that is displayed+enabled
        try:
            candidates = self.driver.find_elements(by, locator)
            for el in candidates:
                if el.is_displayed() and el.is_enabled():
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    except Exception:
                        pass
                    return el
        except Exception:
            pass

        # final fallback: presence wait + return whatever it finds (will raise if not found)
        # If filter controls are collapsed, try toggling the filter panel and retry
        try:
            self.action_click(*self.LOC_FILTER_TOGGLE)
            try:
                el = wait_visible(self.driver, by, locator, 3)
                if el.is_displayed() and el.is_enabled():
                    return el
            except Exception:
                pass
        except Exception:
            pass

        return wait_present(self.driver, by, locator, self.timeout)

    def get_table_row_texts(self) -> list[str]:
        # Return row/card texts from the system users table
        try:
            # wait for at least one row or card to be present
            wait_present(self.driver, *self.LOC_TABLE_ROWS, self.timeout)
        except Exception:
            return []

        results: list[str] = []
        seen: set[str] = set()

        # Prefer structured rows with role='row'
        try:
            rows = self.driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-body')]//div[@role='row']")
            for r in rows:
                try:
                    if not r.is_displayed():
                        continue
                    text = r.text.strip()
                    if text and text not in seen:
                        results.append(text)
                        seen.add(text)
                except Exception:
                    continue
        except Exception:
            pass

        # Also include top-level card elements if present
        try:
            cards = self.driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card') and not(ancestor::div[contains(@class,'oxd-table-card')])]")
            for c in cards:
                try:
                    if not c.is_displayed():
                        continue
                    text = c.text.strip()
                    if text and text not in seen:
                        results.append(text)
                        seen.add(text)
                except Exception:
                    continue
        except Exception:
            pass

        # Fallback: use the original locator if nothing found
        if not results:
            try:
                rows = self.driver.find_elements(*self.LOC_TABLE_ROWS)
                for row in rows:
                    try:
                        if not row.is_displayed():
                            continue
                        text = row.text.strip()
                        if text and text not in seen:
                            results.append(text)
                            seen.add(text)
                    except Exception:
                        continue
            except Exception:
                return []

        return results

    def is_no_records_found_visible(self) -> bool:
        try:
            return self.is_visible(*self.LOC_NO_RECORDS)
        except Exception:
            return False

    def open_add_user_form(self) -> None:
        # Click Add and wait for the Add User form to appear
        self.action_click(*self.LOC_ADD_BUTTON)
        wait_visible(self.driver, *self.LOC_ADD_USER_HEADER, self.timeout)

    def is_add_user_form_loaded(self) -> bool:
        fields = [
            self.LOC_ADD_USER_HEADER,
            self.LOC_ADD_USER_ROLE,
            self.LOC_ADD_EMPLOYEE_NAME,
            self.LOC_ADD_STATUS,
            self.LOC_ADD_USERNAME,
            self.LOC_ADD_PASSWORD,
            self.LOC_ADD_CONFIRM_PASSWORD,
        ]
        return all(self.is_visible(*field) for field in fields)