from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.wait_helpers import wait_visible, wait_url_contains


class TimePage(BasePage):
    
    LOC_EMPLOYEE_TIMESHEETS_HEADER = (By.XPATH, "//h6[contains(normalize-space(), 'Timesheet')] | //*[normalize-space()='Employee Timesheets'] | //div[contains(@class, 'page-title-container')]")
    LOC_EMPLOYEE_NAME_FILTER = (
        By.XPATH,
        "//input[@placeholder='Type for hints...'] | //label[contains(normalize-space(), 'Employee')]/..//input",
    )
    LOC_DROPDOWN_OPTIONS = (By.CSS_SELECTOR, ".oxd-dropdown-option")
    LOC_SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search'] | //button[contains(text(), 'Search')]")
    LOC_TIMESHEET_TABLE = (By.XPATH, "//table[@role='table'] | //table")
    LOC_INVALID_FIELD_ERROR = (By.XPATH, "//span[contains(@class, 'oxd-input-field-error')] | //span[contains(@class, 'error')]")
    LOC_NO_RECORDS_FOUND = (By.XPATH, "//*[contains(normalize-space(), 'No Records')]")

    def __init__(self, driver):
        super().__init__(driver)
        self.timeout = 15

    def is_employee_timesheets_loaded(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_EMPLOYEE_TIMESHEETS_HEADER, self.timeout)
            wait_visible(self.driver, *self.LOC_EMPLOYEE_NAME_FILTER, self.timeout)
            return True
        except Exception:
            return False

    def search_employee(self, employee_name: str) -> None:
        # Search for an employee by name using the timesheets search input
        wait_visible(self.driver, *self.LOC_EMPLOYEE_NAME_FILTER, self.timeout)
        self.action_clear_and_type(*self.LOC_EMPLOYEE_NAME_FILTER, employee_name)
        
        try:
            self.action_click(*self.LOC_SEARCH_BUTTON)
        except Exception:
            search_input = wait_visible(self.driver, *self.LOC_EMPLOYEE_NAME_FILTER, self.timeout)
            search_input.send_keys("\n")

    def search_employee_and_select_from_dropdown(self, employee_name: str) -> None:
        # Type into the employee field and select matching autocomplete option if present
        wait_visible(self.driver, *self.LOC_EMPLOYEE_NAME_FILTER, self.timeout)
        self.action_clear_and_type(*self.LOC_EMPLOYEE_NAME_FILTER, employee_name)
        
        def options_available(driver):
            options = driver.find_elements(By.XPATH, "//div[contains(@class, 'oxd-autocomplete-option')]")
            return [o for o in options if o.is_displayed() and o.text.strip()]
        
        try:
            options = WebDriverWait(self.driver, self.timeout).until(options_available)
            if options:
                for opt in options:
                    if employee_name.lower() in opt.text.lower():
                        try:
                            opt.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", opt)
                        return
                try:
                    options[0].click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", options[0])
        except Exception:
            pass

    def get_timesheet_records(self) -> list[str]:
        # Return timesheet table row texts
        try:
            wait_visible(self.driver, *self.LOC_TIMESHEET_TABLE, self.timeout)
            rows = self.driver.find_elements(By.XPATH, "//table[@role='table']//tbody//tr")
            return [row.text for row in rows if row.text.strip()]
        except Exception:
            return []

    def is_invalid_field_error_visible(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_INVALID_FIELD_ERROR, self.timeout)
            return True
        except Exception:
            return False

    def is_no_records_found_visible(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_NO_RECORDS_FOUND, self.timeout)
            return True
        except Exception:
            return False

    def is_customer_list_loaded(self) -> bool:
        try:
            wait_url_contains(self.driver, "viewCustomers", self.timeout)
            return (
                self.is_text_visible("Customer")
            )
        except Exception:
            return False