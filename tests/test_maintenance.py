from __future__ import annotations

import pytest

from pages.dashboard_page import DashboardPage

from pages.maintenance_page import MaintenancePage

def test_maintenance_requires_password_prompt(logged_in_driver):
    """FR-MAINT-01: Navigating to Maintenance must display a password confirmation prompt before granting access."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_click_sidebar_item("Maintenance")

    page = MaintenancePage(logged_in_driver)
    assert page.is_password_prompt_visible(), "Expected admin password confirmation prompt when opening Maintenance"