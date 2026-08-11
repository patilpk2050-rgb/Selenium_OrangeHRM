from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.wait_helpers import wait_visible, wait_present
"""Page object for Directory search and employee card interactions."""


class DirectoryPage(BasePage):
    LOC_PAGE_HEADER = (By.XPATH, "//h6[contains(normalize-space(),'Directory')] | //h5[contains(normalize-space(),'Directory')]")
    LOC_SEARCH_INPUT = (By.XPATH, "//input[@placeholder='Type for hints...' or @placeholder='Type for hints']")
    LOC_SEARCH_BUTTON = (By.XPATH, "//button[normalize-space()='Search'] | //button[contains(., 'Search')]")
    LOC_RECORDS_FOUND = (By.XPATH, "//*[contains(text(),'Records Found') or contains(text(),'records found')]")
    # fallback locators to find employee cards / names
    LOC_CARD_CANDIDATES = [
        (By.XPATH, "//div[contains(@class,'orangehrm-directory-card')]"),
        (By.XPATH, "//div[contains(@class,'oxd-card') and .//img]") ,
        (By.XPATH, "//div[contains(@class,'oxd-table-card')]") ,
        (By.XPATH, "//div[contains(@class,'employee-card')]") ,
        (By.XPATH, "//div[contains(@class,'directory-card')]") ,
    ]

    def is_directory_loaded(self) -> bool:
        try:
            wait_visible(self.driver, *self.LOC_PAGE_HEADER, self.timeout)
            # also accept records found or cards present
            try:
                wait_visible(self.driver, *self.LOC_RECORDS_FOUND, 3)
                return True
            except Exception:
                # check for any candidate card
                for loc in self.LOC_CARD_CANDIDATES:
                    els = self.driver.find_elements(*loc)
                    if els:
                        return True
                return True
        except Exception:
            return False

    def get_employee_card_elements(self) -> list[WebElement]:
        # Return the first non-empty list of employee card elements found on the page
        for loc in self.LOC_CARD_CANDIDATES:
            els = self.driver.find_elements(*loc)
            if els:
                visible = [e for e in els if e.is_displayed()]
                if visible:
                    return visible

        # fallback: generic card-like containers used by OrangeHRM variants
        generic_candidates = [
            (By.XPATH, "//div[contains(@class,'oxd-grid-item') and .//img]"),
            (By.XPATH, "//div[contains(@class,'oxd-sheet') and .//img]"),
            (By.XPATH, "//div[contains(@class,'oxd-card') and (.//img or .//svg)]"),
            (By.XPATH, "//div[contains(@class,'directory-card')]"),
            (By.XPATH, "//div[contains(@class,'employee-card')]"),
        ]
        for by, locator in generic_candidates:
            try:
                els = self.driver.find_elements(by, locator)
                visible = [e for e in els if e.is_displayed()]
                if visible:
                    return visible
            except Exception:
                continue

        # fallback: look for autocomplete/suggestion items (typeahead results)
        try:
            suggs = self.driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-autocomplete-dropdown')]//div[.//span or .//p or .//div]")
            visible = [s for s in suggs if s.is_displayed() and s.text.strip()]
            if visible:
                return visible
        except Exception:
            pass

        # last resort: look for image tiles in the page and return their parents
        imgs = self.driver.find_elements(By.XPATH, "//img")
        try:
            parents = []
            for i in imgs:
                if i.is_displayed() and i.get_attribute('src'):
                    try:
                        parents.append(i.find_element(By.XPATH, ".."))
                    except Exception:
                        pass
            if parents:
                return parents
        except Exception:
            pass
        return []

    def get_card_name(self, card: WebElement) -> str:
        # Extract a human-readable name from a card element
        candidates = [
            ".//h3", ".//h4", ".//h6", ".//p", ".//span",
            ".//div//h3", ".//div//h4", ".//div//h6", ".//a",
            ".//*[@alt or @title or @data-tooltip]",
        ]
        for c in candidates:
            try:
                el = card.find_element(By.XPATH, c)
                text = (el.get_attribute("textContent") or el.text or "").strip()
                if text:
                    return text
            except Exception:
                continue
        text = (card.get_attribute("textContent") or card.text or "").strip()
        return text

    def card_has_avatar(self, card: WebElement) -> bool:
        try:
            imgs = card.find_elements(By.XPATH, ".//img | .//svg | .//*[contains(@class,'avatar') or contains(@class,'profile')]" )
            if any(i.is_displayed() for i in imgs):
                return True
            for attr in ["src", "data-src", "alt", "title", "aria-label"]:
                value = card.get_attribute(attr)
                if value and any(token in str(value).lower() for token in ["avatar", "profile", "person", "user"]):
                    return True
            return False
        except Exception:
            return False

    def search_by_employee_name(self, name: str) -> None:
        # Perform a directory search by employee name and wait for results/cards
        try:
            self.driver.set_window_size(1920, 1080)
        except Exception:
            pass
        try:
            self.driver.execute_script("document.body.style.zoom='100%'")
        except Exception:
            pass

        try:
            self.action_clear_and_type(*self.LOC_SEARCH_INPUT, name)
        except Exception:
            el = self.driver.find_element(*self.LOC_SEARCH_INPUT)
            self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", el, name)
        # try selecting autocomplete suggestion if it appears
        try:
            # press Enter to submit if widget expects it
            inp = self.driver.find_element(*self.LOC_SEARCH_INPUT)
            try:
                inp.send_keys(Keys.ENTER)
            except Exception:
                pass
        except Exception:
            pass

        try:
            self.action_click(*self.LOC_SEARCH_BUTTON)
        except Exception:
            pass

        # wait for either cards, records found, or autocomplete suggestions
        def results_ready(driver):
            # records found
            try:
                if driver.find_elements(*self.LOC_RECORDS_FOUND):
                    return True
            except Exception:
                pass
            # any card candidate present
            try:
                for loc in self.LOC_CARD_CANDIDATES:
                    if driver.find_elements(*loc):
                        return True
            except Exception:
                pass
            # autocomplete dropdown options
            try:
                opts = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-autocomplete-dropdown')]//div[.//span or .//p or .//div]")
                if opts:
                    return True
            except Exception:
                pass
            return False

        try:
            # Wait up to timeout for either generic results, or specifically
            # for a card that contains the searched name.
            def ready_or_name_present(driver):
                if results_ready(driver):
                    # quick check for the name in any visible card
                    try:
                        cards = self.get_employee_card_elements()
                        for c in cards:
                            try:
                                if name.lower() in self.get_card_name(c).lower():
                                    return True
                            except Exception:
                                continue
                    except Exception:
                        pass
                    return True
                return False

            WebDriverWait(self.driver, self.timeout).until(ready_or_name_present)
        except Exception:
            pass

    def click_employee_by_name(self, name: str) -> bool:
        # Click the employee card or suggestion that matches the provided name
        cards = self.get_employee_card_elements()
        for c in cards:
            txt = self.get_card_name(c)
            if txt and name.lower() in txt.lower():
                try:
                    link = c.find_element(By.XPATH, ".//a[normalize-space()=\"%s\"]" % txt)
                    if link.is_displayed():
                        link.click()
                        return True
                except Exception:
                    try:
                        # click the card itself
                        c.click()
                        return True
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", c)
                            return True
                        except Exception:
                            return False
        # if not found in cards, try autocomplete suggestion items
        try:
            options = self.driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-autocomplete-dropdown')]//div[.//span or .//p or .//div]")
            for o in options:
                try:
                    if name.lower() in o.text.strip().lower():
                        if o.is_displayed():
                            o.click()
                            return True
                except Exception:
                    try:
                        self.driver.execute_script("arguments[0].click();", o)
                        return True
                    except Exception:
                        continue
        except Exception:
            pass

        return False

    def is_invalid_search_error_visible(self) -> bool:
        # consider required-field errors or a 'No Records Found' message as the negative indicator
        try:
            if self.get_required_error_count() > 0:
                return True
        except Exception:
            pass

        try:
            no_rec = self.driver.find_element(By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'no records found') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'no records available')]")
            if no_rec and no_rec.text.strip():
                return True
        except Exception:
            pass

        return False