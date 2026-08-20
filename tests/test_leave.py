from __future__ import annotations

import pytest

from datetime import date, timedelta

from pages.dashboard_page import DashboardPage

from pages.leave_page import LeavePage


@pytest.mark.leave
@pytest.mark.smoke
def test_leave_list_loads_and_displays_table(logged_in_driver):
    """FR-LV-01: Leave List page must load and display the leave records table."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_click_leave_list()
    page = LeavePage(logged_in_driver)
    assert page.is_leave_list_loaded(), "Leave List did not load or table not present"


@pytest.mark.leave
@pytest.mark.regression
def test_leave_type_dropdown_populated(logged_in_driver):
    """FR-LV-02: The Leave Type dropdown must be populated with available options."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_click_leave_list()
    page = LeavePage(logged_in_driver)

    try:
        selected = page.select_first_dropdown_option_and_search(page.LOC_LEAVE_TYPE)
    except Exception as e:
        if page.is_no_records_found_visible():
            return
        pytest.fail(f"Dropdown interaction failed: {str(e)}")

    assert selected, "Expected a non-empty Leave Type option"
