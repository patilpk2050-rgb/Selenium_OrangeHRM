from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.wait_helpers import wait_visible, wait_present

"""Page object for the My Info section: personal and contact details."""


class MyInfoPage(BasePage):
    LOC_PERSONAL_TAB = (By.XPATH, "//a[normalize-space()='Personal Details'] | //h6[normalize-space()='Personal Details']")
    LOC_CONTACT_TAB = (By.XPATH, "//a[normalize-space()='Contact Details']")
    LOC_DEPENDANTS_TAB = (By.XPATH, "//a[normalize-space()='Dependents'] | //a[normalize-space()='Dependants']")
    LOC_IMMIGRATION_TAB = (By.XPATH, "//a[normalize-space()='Immigration']")
    LOC_QUALIFICATIONS_TAB = (By.XPATH, "//a[normalize-space()='Qualifications']")

    # Personal details fields (flexible: input or span)
    LOC_FULLNAME = (
            By.XPATH,
            "//h6[contains(normalize-space(),'Personal Details')] | //label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//span | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//span",
    )
    LOC_EMPLOYEE_ID = (By.XPATH, "//label[normalize-space()='Employee Id']/../following-sibling::div//span | //label[normalize-space()='Employee Id']/../following-sibling::div//input")
    LOC_DOB = (By.XPATH, "//label[contains(normalize-space(),'Date of Birth')]/../following-sibling::div//input | //label[contains(normalize-space(),'Date of Birth')]/../following-sibling::div//span")
    # Name fields: the form sometimes groups First/Middle/Last under a single
    # "Employee Full Name" label. Use positional fallbacks and label fallbacks
    # so locators are tolerant across UI variants.
    LOC_FIRST_NAME = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//span | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//span | //label[normalize-space()='First Name']/../following-sibling::div//input | //label[normalize-space()='First Name']/../following-sibling::div//span)[1]",
    )
    LOC_MIDDLE_NAME = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//span | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//span | //label[normalize-space()='Middle Name']/../following-sibling::div//input | //label[normalize-space()='Middle Name']/../following-sibling::div//span)[2]",
    )
    LOC_LAST_NAME = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Employee Full Name')]/../following-sibling::div//span | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//input | //label[contains(normalize-space(),'Full Name')]/../following-sibling::div//span | //label[normalize-space()='Last Name']/../following-sibling::div//input | //label[normalize-space()='Last Name']/../following-sibling::div//span)[3]",
    )
    LOC_GENDER = (By.XPATH, "//label[normalize-space()='Gender']/../following-sibling::div//span | //label[normalize-space()='Gender']/../following-sibling::div//input")
    LOC_NATIONALITY = (By.XPATH, "//label[normalize-space()='Nationality']/../following-sibling::div//span | //label[normalize-space()='Nationality']/../following-sibling::div//input")
    LOC_MARITAL_STATUS = (By.XPATH, "//label[normalize-space()='Marital Status']/../following-sibling::div//span | //label[normalize-space()='Marital Status']/../following-sibling::div//input")
    LOC_SAVE_BUTTON = (By.XPATH, "//button[normalize-space()='Save']")

    # Contact details
    LOC_ADDRESS = (By.XPATH, "//label[contains(normalize-space(),'Address')]/../following-sibling::div//textarea | //label[contains(normalize-space(),'Address')]/../following-sibling::div//input")
    LOC_TELEPHONE = (By.XPATH, "//label[contains(normalize-space(),'Telephone')]/../following-sibling::div//input")
    LOC_MOBILE = (By.XPATH, "//label[contains(normalize-space(),'Mobile')]/../following-sibling::div//input")
    LOC_WORK_EMAIL = (By.XPATH, "//label[contains(normalize-space(),'Work Email')]/../following-sibling::div//input | //label[contains(normalize-space(),'Work Email')]/../following-sibling::div//span")

    # Dependents
    LOC_DEPENDANTS_ADD = (By.XPATH, "//button[normalize-space()='Add'] | //a[normalize-space()='Add']")

    # Immigration (generic check)
    LOC_IMMIGRATION_HEADER = (By.XPATH, "//h6[normalize-space()='Immigration'] | //h3[normalize-space()='Immigration']")

    # Qualifications -> Work Experience
    LOC_QUALIFICATIONS_SECTION = (By.XPATH, "//h6[normalize-space()='Qualifications'] | //a[normalize-space()='Qualifications']")
    LOC_WORK_EXPERIENCE_ADD = (By.XPATH, "//button[contains(normalize-space(),'Add') and contains(., 'Work')] | //section//button[normalize-space()='Add']")
    LOC_WORK_COMPANY = (By.XPATH, "//label[contains(normalize-space(),'Company')]/../following-sibling::div//input")
    LOC_WORK_TITLE = (By.XPATH, "//label[contains(normalize-space(),'Job Title')]/../following-sibling::div//input")
    LOC_WORK_FROM = (By.XPATH, "//label[contains(normalize-space(),'From')]/../following-sibling::div//input")
    LOC_WORK_TO = (By.XPATH, "//label[contains(normalize-space(),'To')]/../following-sibling::div//input")
    LOC_WORK_SAVE = (By.XPATH, "//button[normalize-space()='Save'] | //button[normalize-space()='Add']")
    LOC_WORK_ROWS = (By.XPATH, "//div[contains(@class,'oxd-table-body')]//div[@role='row']")

    def is_personal_details_loaded(self) -> bool:
        # Verify the Personal Details tab is loaded by checking key fields
        try:
            # Ensure the Personal Details tab is active if present
            try:
                if self.is_visible(*self.LOC_PERSONAL_TAB):
                    try:
                        self.action_click(*self.LOC_PERSONAL_TAB)
                    except Exception:
                        pass
            except Exception:
                pass

            # Allow a short grace period for the Personal Details content to render
            try:
                wait_present(self.driver, *self.LOC_FULLNAME, min(self.timeout, 5))
            except Exception:
                # fallback to a slightly longer wait once more
                wait_present(self.driver, *self.LOC_FULLNAME, self.timeout)
            # check key fields: accept if at least two are visible to handle UI variations
            fields = [self.LOC_EMPLOYEE_ID, self.LOC_DOB, self.LOC_GENDER, self.LOC_NATIONALITY, self.LOC_MARITAL_STATUS]
            visible_count = 0
            for f in fields:
                try:
                    if self.is_visible(*f):
                        visible_count += 1
                except Exception:
                    continue
            return visible_count >= 2
        except Exception:
            return False

    def open_contact_details(self) -> None:
        # Activate the Contact Details tab and wait for the work email field
        self.action_click(*self.LOC_CONTACT_TAB)
        wait_visible(self.driver, *self.LOC_WORK_EMAIL, self.timeout)

    def set_work_email_and_save(self, email: str) -> None:
        # Set the Work Email field and save to trigger validation
        try:
            el = self.driver.find_element(*self.LOC_WORK_EMAIL)

            js_set_email = (
                "(function(el,email){"
                "try{ if(el.tagName && el.tagName.toLowerCase()==='input'){ el.value=''; } else { if(el.querySelector){ var inp0 = el.querySelector('input'); if(inp0) inp0.value=''; } } }catch(e){}"
                "try{"
                " if(el.tagName && el.tagName.toLowerCase()==='input'){ el.value = email; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }"
                " else { try{ el.textContent = email; }catch(e){} var candidate = null; try{ candidate = el.querySelector && el.querySelector('input'); }catch(e){ candidate = null; } if(!candidate){ try{ candidate = el.closest && el.closest('div') && el.closest('div').querySelector('input'); }catch(e){ candidate = null; } } if(candidate){ candidate.value = email; candidate.dispatchEvent(new Event('input')); candidate.dispatchEvent(new Event('change')); } }"
                "}catch(e){} })(arguments[0], arguments[1]);"
            )

            # Try normal clear/send_keys first, fall back to JS setter if that fails
            try:
                try:
                    el.clear()
                except Exception:
                    pass
                try:
                    el.send_keys(email)
                except Exception:
                    self.driver.execute_script(js_set_email, el, email)
            except Exception:
                self.driver.execute_script(js_set_email, el, email)

            # ensure blur/commit
            try:
                el.send_keys('\t')
            except Exception:
                try:
                    self.driver.execute_script('arguments[0].blur();', el)
                except Exception:
                    pass

            self.action_click(*self.LOC_SAVE_BUTTON)
        except Exception:
            raise

    def wait_for_validation_errors(self, timeout: int = 5) -> int:
        import time
        from selenium.webdriver.common.by import By

        # Poll short intervals for visible validation messages or aria-invalid markers
        end = time.time() + timeout
        while time.time() < end:
            # count visible error message elements
            try:
                msg_count = len(self.driver.find_elements(*self.LOC_REQUIRED_ERRORS))
            except Exception:
                msg_count = 0

            # count inputs marked aria-invalid
            try:
                invalids = len(self.driver.find_elements(By.CSS_SELECTOR, "[aria-invalid=\"true\"]"))
            except Exception:
                invalids = 0

            total = msg_count + invalids
            if total > 0:
                return total
            time.sleep(0.5)
        return 0

    def open_dependants_tab(self) -> None:
        self.action_click(*self.LOC_DEPENDANTS_TAB)

    def has_dependants_add(self) -> bool:
        try:
            return self.is_visible(*self.LOC_DEPENDANTS_ADD)
        except Exception:
            return False

    def open_immigration_tab(self) -> None:
        self.action_click(*self.LOC_IMMIGRATION_TAB)

    def has_immigration_fields(self) -> bool:
        try:
            if self.is_visible(*self.LOC_IMMIGRATION_HEADER):
                return True
            # alternative checks: passport/number labels or table rows under immigration
            alt = (
                By.XPATH,
                "//label[contains(normalize-space(),'Passport')]|//label[contains(normalize-space(),'Immigration')]|//h6[contains(normalize-space(),'Immigration Records')]",
            )
            return self.is_visible(*alt)
        except Exception:
            return False

    def open_qualifications_tab(self) -> None:
        self.action_click(*self.LOC_QUALIFICATIONS_TAB)

    def add_work_experience(self, company: str, title: str, frm: str, to: str) -> None:
        try:
            # Try clicking the Add button scoped to Work Experience
            try:
                header_add = (
                    By.XPATH,
                    "//h6[normalize-space()='Work Experience']/following::button[normalize-space()='Add'][1]",
                )
                self.action_click(*header_add)
            except Exception:
                try:
                    self.action_click(*self.LOC_WORK_EXPERIENCE_ADD)
                except Exception:
                    # fallback: click any Add button
                    self.action_click(*self.LOC_WORK_SAVE)

            # Wait for fields to appear (company/title)
            try:
                wait_present(self.driver, *self.LOC_WORK_COMPANY, self.timeout)
            except Exception:
                pass

            self.action_clear_and_type(*self.LOC_WORK_COMPANY, company)
            self.action_clear_and_type(*self.LOC_WORK_TITLE, title)
            self.action_clear_and_type(*self.LOC_WORK_FROM, frm)
            self.action_clear_and_type(*self.LOC_WORK_TO, to)
            self.action_click(*self.LOC_WORK_SAVE)
            # small wait for save to complete
            import time

            time.sleep(1)
        except Exception:
            raise

    def get_work_experience_rows(self) -> list[str]:
        try:
            wait_present(self.driver, *self.LOC_WORK_ROWS, self.timeout)
        except Exception:
            return []
        rows = self.driver.find_elements(*self.LOC_WORK_ROWS)
        return [r.text.strip() for r in rows if r.is_displayed() and r.text.strip()]