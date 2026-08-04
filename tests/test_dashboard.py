from __future__ import annotations

import pytest

from pages.dashboard_page import DashboardPage

def test_dashboard_header_visible_after_login(logged_in_driver):
    """FR-DASH-01: After login, Dashboard heading must be visible."""
    dashboard_page = DashboardPage(logged_in_driver)

    assert dashboard_page.get_header_text() == "Dashboard"

def test_dashboard_main_widgets_visible(logged_in_driver):
    """FR-DASH-02, FR-DASH-03: Time at Work and My Actions widgets must be visible."""
    dashboard_page = DashboardPage(logged_in_driver)

    assert dashboard_page.is_time_at_work_visible(), (
        "Time at Work widget is not visible."
    )
    assert dashboard_page.is_my_actions_visible(), (
        "My Actions widget is not visible."
    )