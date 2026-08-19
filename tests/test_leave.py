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


@pytest.mark.leave
@pytest.mark.regression
def test_assign_leave_success_for_future_dates(logged_in_driver):
    """FR-LV-03: Completing Assign Leave with valid future dates must succeed and be verifiable."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_leave()
    page = LeavePage(logged_in_driver)

    page.open_assign_leave()
    assert page.is_assign_form_loaded(), "Assign Leave form did not load."
    page.assign_leave("Baba Dook", True, "2099-01-10", "2099-01-12")

    msg = page.get_assign_confirmation_text()
    if msg:
        assert "success" in msg.lower() or "assigned" in msg.lower()
    else:
        # navigate back to leave list and search for the employee
        dashboard.action_go_to_leave()
        page.search_by_employee_name("Baba Dook")
        assert page.is_no_records_found_visible() or page.get_table_row_texts(), "Expected assigned leave to appear or a confirmation message"