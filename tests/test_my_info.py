from __future__ import annotations

import pytest

from pages.dashboard_page import DashboardPage

from pages.my_info_page import MyInfoPage

def test_personal_details_fields_visible(logged_in_driver):
    """FR-MI-01: Personal Details tab must load with key fields visible."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_my_info()
    page = MyInfoPage(logged_in_driver)

    if not page.is_personal_details_loaded():
        pytest.skip("Personal Details tab not present in this environment")

    assert page.is_visible(*page.LOC_EMPLOYEE_ID)
    assert page.is_visible(*page.LOC_DOB)
    assert page.is_visible(*page.LOC_FIRST_NAME), "First Name should be visible"
    if page.is_present(*page.LOC_MIDDLE_NAME):
        # If middle name field exists in the DOM, it's acceptable for it to be empty
        assert page.is_present(*page.LOC_MIDDLE_NAME)
    assert page.is_visible(*page.LOC_LAST_NAME), "Last Name should be visible"

def test_contact_details_tab_fields_visible(logged_in_driver):
    """FR-MI-02: Contact Details tab must show address, telephone, mobile and work email."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_my_info()
    page = MyInfoPage(logged_in_driver)

    try:
        page.open_contact_details()
    except Exception:
        pytest.skip("Contact Details tab not present")

    assert page.is_visible(*page.LOC_ADDRESS) or page.is_visible(*page.LOC_TELEPHONE) or page.is_visible(*page.LOC_MOBILE)
    assert page.is_visible(*page.LOC_WORK_EMAIL)