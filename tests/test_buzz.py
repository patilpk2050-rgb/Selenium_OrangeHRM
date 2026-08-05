from __future__ import annotations

import pytest

from pages.dashboard_page import DashboardPage

from pages.buzz_page import BuzzPage

def test_buzz_feed_loads_with_existing_post(logged_in_driver):
    """FR-BUZZ-01: Buzz feed page must load and display the post feed with at least one existing post."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_buzz()

    page = BuzzPage(logged_in_driver)
    assert page.is_buzz_loaded(), "Buzz feed did not load or no feed element found ('.orangehrm-buzz')"