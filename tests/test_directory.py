from __future__ import annotations
from typing import Any

import pytest

from selenium.webdriver.common.by import By

import time

from pages.dashboard_page import DashboardPage

from pages.directory_page import DirectoryPage


@pytest.mark.directory
@pytest.mark.smoke
def test_directory_page_loads_and_displays_employee_cards(logged_in_driver: Any):
    """FR-DIR-01: Directory page must load and display employee cards without any search filter applied."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_directory()

    page = DirectoryPage(logged_in_driver)
    assert page.is_directory_loaded(), "Directory page did not load or no cards found"

    cards = page.get_employee_card_elements()
    assert cards, "Expected at least one employee card to be present on Directory"
