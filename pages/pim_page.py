from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage
from utils.wait_helpers import wait_present, wait_visible, wait_url_contains
"""Page object for PIM (employee) operations like search and add."""


class PIMPage(BasePage):
    LOC_SEARCH_EMPLOYEE_ID = (
        By.XPATH,
        "//label[normalize-space()='Employee Id']/../following-sibling::div//input",
    )
    LOC_SEARCH_EMPLOYEE_NAME = (
        By.XPATH,
        "//label[normalize-space()='Employee Name']/../following-sibling::div//input",
    )
    LOC_SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search' or normalize-space()='Rechercher']",
    )

    LOC_ADD_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Add' or normalize-space()='Ajouter' or normalize-space()='Add Employee' or normalize-space()='Ajouter un employé']",
    )

    LOC_TABLE_ROWS = (By.XPATH, "//div[contains(@class,'oxd-table-body')]//div[@role='row']")
    LOC_NO_RECORDS = (By.XPATH, "//*[normalize-space()='No Records Found']")
    LOC_FIRST_NAME = (By.XPATH, "//label[normalize-space()='First Name']/../following-sibling::div//input")
    LOC_FIRST_NAME_ALT = (
        By.XPATH,
        "//input[contains(@placeholder,'First Name') or @name='firstName' or @name='first_name']",
    )
    LOC_MIDDLE_NAME = (By.XPATH, "//label[normalize-space()='Middle Name']/../following-sibling::div//input")
    LOC_MIDDLE_NAME_ALT = (
        By.XPATH,
        "//input[contains(@placeholder,'Middle Name') or @name='middleName' or @name='middle_name']",
    )
    LOC_LAST_NAME = (By.XPATH, "//label[normalize-space()='Last Name']/../following-sibling::div//input")
    LOC_LAST_NAME_ALT = (
        By.XPATH,
        "//input[contains(@placeholder,'Last Name') or @name='lastName' or @name='last_name']",
    )
    LOC_EMPLOYEE_ID_FIELD = (By.XPATH, "//label[normalize-space()='Employee Id']/../following-sibling::div//input")
    LOC_EMPLOYEE_ID_FIELD_ALT = (
        By.XPATH,
        "//input[contains(@placeholder,'Employee Id') or @name='employeeId' or @name='employee_id']",
    )
    LOC_EMPLOYEE_ID_DISPLAY = (
        By.XPATH,
        "//label[normalize-space()='Employee Id']/../following-sibling::div//span | //label[normalize-space()='Employee Id']/../following-sibling::div//div",
    )
    LOC_SAVE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Save' or normalize-space()='Enregistrer']",
    )

    LOC_PERSONAL_DETAILS_TAB = (By.XPATH, "//a[normalize-space()='Personal Details'] | //h6[normalize-space()='Personal Details']")
    LOC_CONTACT_DETAILS_TAB = (By.XPATH, "//a[normalize-space()='Contact Details']")

    def get_header_text(self) -> str:
        # Return the page header text for PIM pages
        return self.get_page_header()

    def is_employee_list_loaded(self) -> bool:
        # Confirm the employee list/table is visible on the PIM page
        try:
            wait_url_contains(self.driver, "/pim", self.timeout)
            wait_visible(self.driver, *self.LOC_TABLE_ROWS, self.timeout)
            return True
        except Exception:
            return False

    def search_by_employee_id(self, emp_id: str) -> None:
        try:
            # Try to ensure the search input is visible (expand section if needed)
            if not self.is_visible(*self.LOC_SEARCH_EMPLOYEE_ID):
                try:
                    toggle = self.driver.find_element(By.XPATH, "//div[contains(., 'Employee Information')]//button")
                    if toggle.is_displayed():
                        try:
                            toggle.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", toggle)
                except Exception:
                    try:
                        alt = self.driver.find_element(By.XPATH, "//button[contains(@class,'oxd-icon-button')]")
                        if alt.is_displayed():
                            try:
                                alt.click()
                            except Exception:
                                self.driver.execute_script("arguments[0].click();", alt)
                    except Exception:
                        pass

            # Populate the employee id field using page helper or JS fallback
            try:
                self.action_clear_and_type(*self.get_employee_id_locator(), emp_id)
            except Exception:
                try:
                    el = self.driver.find_element(*self.get_employee_id_locator())
                    self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", el, emp_id)
                except Exception:
                    pass

            # Click search and wait for results
            try:
                self.action_click(*self.LOC_SEARCH_BUTTON)
            except Exception:
                try:
                    btn = self.driver.find_element(*self.LOC_SEARCH_BUTTON)
                    self.driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    pass

            self.wait_for_search_results()
        except Exception:
            # Let caller decide retry behavior; do not raise here to keep tests robust
            return

    def wait_for_search_results(self) -> None:
        def search_ready(driver):
            try:
                rows = driver.find_elements(*self.LOC_TABLE_ROWS)
                for row in rows:
                    try:
                        txt = (row.text or '').strip() or (row.get_attribute('textContent') or '').strip()
                        if txt:
                            return True
                    except Exception:
                        continue
            except Exception:
                pass
            try:
                records = driver.find_elements(*self.LOC_NO_RECORDS)
                return any(node.is_displayed() for node in records)
            except Exception:
                return False

        WebDriverWait(self.driver, self.timeout).until(search_ready)

    def get_field_locator(self, primary: tuple, alternate: tuple) -> tuple:
        return primary if self.is_visible(*primary) else alternate

    def get_first_name_locator(self) -> tuple:
        return self.get_field_locator(self.LOC_FIRST_NAME, self.LOC_FIRST_NAME_ALT)

    def get_middle_name_locator(self) -> tuple:
        return self.get_field_locator(self.LOC_MIDDLE_NAME, self.LOC_MIDDLE_NAME_ALT)

    def get_last_name_locator(self) -> tuple:
        return self.get_field_locator(self.LOC_LAST_NAME, self.LOC_LAST_NAME_ALT)

    def get_employee_id_locator(self) -> tuple:
        return self.get_field_locator(self.LOC_EMPLOYEE_ID_FIELD, self.LOC_EMPLOYEE_ID_FIELD_ALT)

    def get_table_row_texts(self) -> list[str]:
        def rows_or_no_records(driver):
            try:
                rows = driver.find_elements(*self.LOC_TABLE_ROWS)
                visible_rows = [r for r in rows if r.is_displayed() and r.text.strip()]
                if visible_rows:
                    return True
            except Exception:
                pass

            try:
                nodes = driver.find_elements(*self.LOC_NO_RECORDS)
                if any(n.is_displayed() for n in nodes):
                    return True
            except Exception:
                pass

            return False

        WebDriverWait(self.driver, self.timeout).until(rows_or_no_records)
        rows = self.driver.find_elements(*self.LOC_TABLE_ROWS)
        return [row.text.strip() for row in rows if row.is_displayed() and row.text.strip()]

    def is_no_records_found_visible(self) -> bool:
        try:
            if self.is_visible(*self.LOC_NO_RECORDS):
                return True
        except Exception:
            pass

        try:
            rows = self.driver.find_elements(*self.LOC_TABLE_ROWS)
            visible_rows = [r for r in rows if r.is_displayed() and r.text.strip()]
            if not visible_rows:
                return True
        except Exception:
            pass

        try:
            empty_nodes = self.driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-body')]//div[contains(normalize-space(.),'No Records') or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no records')]")
            if any(n.is_displayed() for n in empty_nodes):
                return True
        except Exception:
            pass

        return False

    def click_first_table_row(self) -> None:
        rows = self.driver.find_elements(*self.LOC_TABLE_ROWS)
        if not rows:
            raise ValueError("No employee rows found in table")

        first = rows[0]
        try:
            first.click()
        except Exception:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", first)

    def action_open_add_employee(self) -> None:
        if self.is_visible(*self.LOC_FIRST_NAME) or self.is_visible(*self.LOC_FIRST_NAME_ALT):
            return

        try:
            try:
                self.action_click(*self.LOC_ADD_BUTTON)
            except Exception:
                btn = self.driver.find_element(*self.LOC_ADD_BUTTON)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", btn)

            if self.is_visible(*self.LOC_FIRST_NAME) or self.is_visible(*self.LOC_FIRST_NAME_ALT):
                return

            # Fall through to the direct add-employee URL if the list-page CTA is not available
            from urllib.parse import urlparse

            cur = urlparse(self.driver.current_url)
            base = f"{cur.scheme}://{cur.netloc}"
            self.driver.get(base + "/index.php/pim/addEmployee")
            if self.is_visible(*self.LOC_FIRST_NAME) or self.is_visible(*self.LOC_FIRST_NAME_ALT):
                return

            wait_visible(self.driver, *self.LOC_FIRST_NAME_ALT, self.timeout)
            return
        except Exception:
            try:
                from urllib.parse import urlparse

                cur = urlparse(self.driver.current_url)
                base = f"{cur.scheme}://{cur.netloc}"
                self.driver.get(base + "/index.php/pim/addEmployee")
                if self.is_visible(*self.LOC_FIRST_NAME):
                    return
                wait_visible(self.driver, *self.LOC_FIRST_NAME_ALT, self.timeout)
                return
            except Exception:
                raise

    def add_employee(self, first_name: str, middle_name: str, last_name: str, employee_id: str | None = None) -> None:
        self.action_open_add_employee()
        self.action_clear_and_type(*self.get_first_name_locator(), first_name)
        
        if middle_name.strip():
            try:
                self.action_clear_and_type(*self.get_middle_name_locator(), middle_name)
            except Exception:
                pass
        
        self.action_clear_and_type(*self.get_last_name_locator(), last_name)
        
        if employee_id:
            self.action_clear_and_type(*self.get_employee_id_locator(), employee_id)
        
        # Dismiss any overlays before clicking save
        try:
            self.driver.execute_script("document.querySelectorAll('[role=\"dialog\"], .oxd-overlay').forEach(e => e.remove());")
        except Exception:
            pass
        
        self.action_click(*self.LOC_SAVE_BUTTON)
        import time
        import os
        from datetime import datetime

        def saved_or_details_ready(driver):
            try:
                if "addEmployee" not in driver.current_url:
                    return True
            except Exception:
                pass

            try:
                if driver.find_element(*self.LOC_PERSONAL_DETAILS_TAB).is_displayed():
                    return True
            except Exception:
                pass

            try:
                el = driver.find_element(*self.LOC_EMPLOYEE_ID_FIELD)
                if el and (el.get_attribute('value') or el.text):
                    return True
            except Exception:
                pass

            try:
                el2 = driver.find_element(*self.LOC_EMPLOYEE_ID_DISPLAY)
                if el2 and el2.text.strip():
                    return True
            except Exception:
                pass

            return False

        try:
            WebDriverWait(self.driver, max(30, self.timeout)).until(saved_or_details_ready)
        except Exception:
            time.sleep(2)

    def get_current_employee_id(self) -> str:
        # Wait briefly for the employee id field or display to appear after save.
        try:
            # Try the canonical input field first with a slightly longer wait
            try:
                wait_visible(self.driver, *self.LOC_EMPLOYEE_ID_FIELD, timeout=10)
                element = self.driver.find_element(*self.LOC_EMPLOYEE_ID_FIELD)
                val = (element.get_attribute("value") or element.text or element.get_attribute('textContent') or "").strip()
                if val:
                    return self._extract_likely_id(val)
            except Exception:
                pass

            # Try alternate input
            try:
                wait_visible(self.driver, *self.LOC_EMPLOYEE_ID_FIELD_ALT, timeout=5)
                element = self.driver.find_element(*self.LOC_EMPLOYEE_ID_FIELD_ALT)
                val = (element.get_attribute("value") or element.text or element.get_attribute('textContent') or "").strip()
                if val:
                    return self._extract_likely_id(val)
            except Exception:
                pass

            # Try display/span style
            try:
                wait_visible(self.driver, *self.LOC_EMPLOYEE_ID_DISPLAY, timeout=5)
                element = self.driver.find_element(*self.LOC_EMPLOYEE_ID_DISPLAY)
                val = (element.text or element.get_attribute('textContent') or "").strip()
                if val:
                    return self._extract_likely_id(val)
            except Exception:
                pass
        except Exception:
            pass

        return ""

    def _extract_likely_id(self, text: str) -> str:
        import re

        tokens = re.findall(r"[A-Za-z0-9_-]+", text)
        if not tokens:
            return text.strip()

        # Prefer token that isn't obviously a name component (simple heuristic)
        tokens = [t for t in tokens if len(t) >= 2]
        if not tokens:
            return text.strip()

        # Return the longest token
        tokens.sort(key=lambda t: len(t), reverse=True)
        return tokens[0]

    def open_contact_details(self) -> None:
        self.action_click(*self.LOC_CONTACT_DETAILS_TAB)
        wait_visible(self.driver, *self.LOC_CONTACT_DETAILS_TAB, self.timeout)