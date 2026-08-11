from __future__ import annotations

import pytest

from selenium.webdriver.common.by import By

import time

from pages.dashboard_page import DashboardPage

from pages.directory_page import DirectoryPage

def test_directory_page_loads_and_displays_employee_cards(logged_in_driver):
    """FR-DIR-01: Directory page must load and display employee cards without any search filter applied."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_directory()

    page = DirectoryPage(logged_in_driver)
    assert page.is_directory_loaded(), "Directory page did not load or no cards found"

    cards = page.get_employee_card_elements()
    assert cards, "Expected at least one employee card to be present on Directory"

def test_directory_cards_display_name_and_avatar(logged_in_driver):
    """FR-DIR-02: Each employee directory card must display a name and avatar when cards are rendered."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_directory()

    page = DirectoryPage(logged_in_driver)
    dir_cards = page.get_employee_card_elements()
    if not dir_cards:
        pytest.skip("No employee cards are rendered on the Directory page in this environment; skipping detailed card checks")

    # verify each card has a name and avatar; cap checks to first 20 to avoid long runs
    limit = min(len(dir_cards), 20)
    for card in dir_cards[:limit]:
        name = page.get_card_name(card)
        assert name, "Employee card missing name"
        assert page.card_has_avatar(card), f"Employee card for '{name}' missing avatar"