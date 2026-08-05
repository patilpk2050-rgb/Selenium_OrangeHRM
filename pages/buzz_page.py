from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage

"""Page object for Buzz (newsfeed) interactions and posting."""
from utils.wait_helpers import wait_visible


class BuzzPage(BasePage):
    LOC_BUZZ_FEED = (By.CSS_SELECTOR, ".orangehrm-buzz")
    LOC_PHOTO_VIDEO_BUTTON = (By.XPATH, "//button[contains(., 'Photo') or contains(., 'Photo/Video') or contains(@aria-label,'photo')]")
    
    
    def is_buzz_loaded(self) -> bool:
        # Check that the Buzz feed container is present and visible
        try:
            wait_visible(self.driver, *self.LOC_BUZZ_FEED, self.timeout)
            return True
        except Exception:
            return False

    def get_post_input_placeholder(self) -> str | None:
        # Return the prompt/placeholder text for the post input area, if available
        try:
            input_xpath = "//textarea[@placeholder=\"What's on your mind?\"] | //input[@placeholder=\"What's on your mind?\"] | //div[contains(@class,'oxd-editor')]//textarea"
            el = wait_visible(self.driver, By.XPATH, input_xpath, self.timeout)
            # prefer placeholder/aria-label/data-placeholder
            for attr in ("placeholder", "aria-label", "data-placeholder", "title"):
                try:
                    val = el.get_attribute(attr)
                    if val and val.strip():
                        return val.strip()
                except Exception:
                    pass

            # fallback: text content for contenteditable or nearby label
            try:
                txt = el.get_attribute("textContent") or el.text
                if txt and txt.strip():
                    return txt.strip()
            except Exception:
                pass

            # try nearby elements that commonly show the prompt
            try:
                sibling = self.driver.find_element(By.XPATH, "//div[contains(@class,'orangehrm-buzz')]//label | //div[contains(@class,'orangehrm-buzz')]//p")
                t = sibling.text.strip()
                if t:
                    return t
            except Exception:
                pass
            return None
        except Exception:
            return None

    def is_photo_video_button_visible(self) -> bool:
        # Check visibility of the Photo/Video share button near the post input
        try:
            wait_visible(self.driver, *self.LOC_PHOTO_VIDEO_BUTTON, self.timeout)
            return True
        except Exception:
            return False

    def is_feed_scrollable(self) -> bool:

        try:
            # get page + viewport heights
            page_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            viewport_height = self.driver.execute_script(
                "return window.innerHeight"
            )

            # if no scrolling needed → treat as pass
            if page_height <= viewport_height:
                return True

            # get initial scroll
            initial_scroll = self.driver.execute_script(
                "return window.pageYOffset"
            )

            # scroll to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script(
                    "return window.pageYOffset"
                ) > initial_scroll
            )

            # final scroll position
            final_scroll = self.driver.execute_script(
                "return window.pageYOffset"
            )

            return final_scroll > initial_scroll

        except Exception:
            return False