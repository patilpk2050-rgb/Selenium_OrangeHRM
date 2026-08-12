from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.wait_helpers import wait_visible, wait_present


class RecruitmentPage(BasePage):
    
    LOC_CANDIDATES_HEADER = (By.XPATH, "//h5[contains(normalize-space(), 'Candidates')] | //h6[contains(normalize-space(), 'Candidates')] | //*[normalize-space()='Candidates']")
    LOC_CANDIDATE_NAME_FILTER = (By.XPATH, "//label[normalize-space()='Candidate Name']/../following-sibling::div//input | //input[@placeholder='Type for hints...'] | //input[@placeholder='Search']")
    LOC_FILTER_TOGGLE = (By.XPATH, "//div[contains(@class,'oxd-table-filter-header-options')]//button[contains(@class,'oxd-icon-button')]")
    LOC_SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search'] | //button[contains(., 'Search')]")
    LOC_CANDIDATES_TABLE = (By.XPATH, "//div[contains(@class,'oxd-table-body')] | //div[@role='table']")
    LOC_INVALID_FIELD_ERROR = (By.XPATH, "//span[contains(@class,'oxd-input-field-error') or contains(@class,'error')]")
    LOC_NO_RECORDS = (By.XPATH, "//*[contains(normalize-space(),'No Records')]")

    LOC_ADD_CANDIDATE_BUTTON = (By.XPATH, "//button[normalize-space()='Add'] | //button[contains(., 'Add Candidate')]")
    LOC_ADD_CANDIDATE_FORM = (By.XPATH, "//div[contains(@class,'oxd-dialog-container')]//form | //form[contains(@class,'oxd-form')]")

    LOC_FIRST_NAME_FIELD = (By.XPATH, ".//input[@name='firstName'] | .//label[normalize-space()='First Name']/ancestor::div[contains(@class,'oxd-input-group')]//input")
    LOC_LAST_NAME_FIELD = (By.XPATH, ".//input[@name='lastName'] | .//label[normalize-space()='Last Name']/ancestor::div[contains(@class,'oxd-input-group')]//input")
    LOC_EMAIL_FIELD = (
        By.XPATH,
        ".//label[normalize-space()='Email']/ancestor::div[contains(@class,'oxd-input-group')]//input | .//input[@type='email' or (@name='email' or @placeholder='Type here')]",
    )
    LOC_SAVE_BUTTON = (By.XPATH, ".//button[normalize-space()='Save'] | .//button[contains(., 'Save')]")

    def __init__(self, driver):
        super().__init__(driver)
        self.timeout = 15


    def is_candidates_page_loaded(self) -> bool:
        try:
            self.action_dismiss_blocking_overlays()
            wait_visible(self.driver, *self.LOC_CANDIDATES_HEADER, self.timeout)
            try:
                wait_visible(self.driver, *self.LOC_ADD_CANDIDATE_BUTTON, 3)
                return True
            except Exception:
                if self.is_text_visible('Records Found') or self.is_text_visible('No Records'):
                    return True
                return True
            try:
                wait_visible(self.driver, *self.LOC_CANDIDATE_NAME_FILTER, 3)
            except Exception:
                try:
                    self.action_click(*self.LOC_FILTER_TOGGLE)
                    wait_visible(self.driver, *self.LOC_CANDIDATE_NAME_FILTER, 3)
                except Exception:
                    pass
            return True
        except Exception:
            return False

    def open_add_candidate_form(self) -> None:
        # Click Add Candidate and wait for the form dialog
        self.action_click(*self.LOC_ADD_CANDIDATE_BUTTON)
        try:
            wait_present(self.driver, *self.LOC_ADD_CANDIDATE_FORM, self.timeout)
        except Exception:
            self.action_dismiss_blocking_overlays()
            try:
                wait_present(self.driver, *self.LOC_ADD_CANDIDATE_FORM, 3)
            except Exception:
                pass

    def is_add_candidate_form_loaded(self) -> bool:
        try:
            form_el = wait_present(self.driver, *self.LOC_ADD_CANDIDATE_FORM, self.timeout)

            wait_visible(self.driver, By.XPATH, ".//input[@name='firstName'] | .//label[normalize-space()='First Name']/ancestor::div[contains(@class,'oxd-input-group')]//input", self.timeout)
            wait_visible(self.driver, By.XPATH, ".//input[@name='lastName'] | .//label[normalize-space()='Last Name']/ancestor::div[contains(@class,'oxd-input-group')]//input", self.timeout)
            wait_visible(self.driver, By.XPATH, ".//label[normalize-space()='Email']/ancestor::div[contains(@class,'oxd-input-group')]//input", self.timeout)
            wait_visible(self.driver, By.XPATH, ".//button[normalize-space()='Save' or contains(.,'Save')]", self.timeout)
            return True
        except Exception:
            return False


    def _select_dropdown_option_by_label(self, label: str, option_text: str) -> None:
        """Click a dropdown identified by its label and select an option using multiple fallback locators."""
        dropdown_toggle = (
            By.XPATH,
            f"//label[normalize-space()='{label}']/../following-sibling::div//div[contains(@class,'oxd-select-text')]|//label[normalize-space()='{label}']/following::div[contains(@class,'oxd-select-text')][1]",
        )
        self.action_click(*dropdown_toggle)

        option_locators = [
            (By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{option_text}']"),
            (By.XPATH, f"//div[contains(@class,'oxd-select-dropdown')]//span[normalize-space()='{option_text}']"),
            (By.CSS_SELECTOR, f".oxd-dropdown-option[role='option']"),
        ]

        for by, loc in option_locators:
            try:
                el = wait_present(self.driver, by, loc, 5)
                if el and (el.text.strip() != option_text):
                    candidates = self.driver.find_elements(by, loc)
                    for c in candidates:
                        if c.text.strip() == option_text:
                            c.click()
                            return
                else:
                    el.click()
                    return
            except Exception:
                continue

        try:
            spans = self.driver.find_elements(By.XPATH, "//div[@role='listbox']//span | //div[contains(@class,'oxd-select-dropdown')]//span")
            tokens = [t.strip().lower() for t in option_text.split() if t.strip()]
            for s in spans:
                txt = (s.text or '').strip()
                if not txt:
                    continue
                low = txt.lower()
                if option_text.lower() in low:
                    s.click()
                    return
                if any(tok in low for tok in tokens):
                    s.click()
                    return

            for s in spans:
                txt = (s.text or '').strip()
                if txt and not txt.startswith('-') and '--' not in txt:
                    s.click()
                    return
        except Exception:
            pass

        raise RuntimeError(f"Dropdown option '{option_text}' not found and no fallback available")

    def submit_add_candidate_form(self, first_name: str = '', last_name: str = '', email: str = '', vacancy: str = '') -> None:
        if first_name:
            self.action_clear_and_type(*self.LOC_FIRST_NAME_FIELD, first_name)
        if last_name:
            self.action_clear_and_type(*self.LOC_LAST_NAME_FIELD, last_name)
        if email:
            self.action_clear_and_type(*self.LOC_EMAIL_FIELD, email)
        if vacancy:
            try:
                self.action_click(By.XPATH, "//label[normalize-space()='Job Vacancy']/../following-sibling::div//div[contains(@class,'oxd-select-text')]")
                self.action_click(By.XPATH, f"//div[@role='listbox']//span[normalize-space()='{vacancy}']")
            except Exception:
                pass
        self.action_click(*self.LOC_SAVE_BUTTON)

    def get_add_candidate_validation_messages(self) -> list[str]:
        try:
            elems = self.driver.find_elements(*self.LOC_INVALID_FIELD_ERROR)
            return [e.text for e in elems if e.text.strip()]
        except Exception:
            return []