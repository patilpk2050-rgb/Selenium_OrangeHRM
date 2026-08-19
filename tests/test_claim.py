from __future__ import annotations

import uuid

import pytest

from selenium.webdriver.common.by import By

from pages.dashboard_page import DashboardPage

from pages.claim_page import ClaimPage

@pytest.mark.claim
def test_submit_claim_page_loads_with_fields(logged_in_driver):
    """FR-CLAIM-01: Employee Claims page must load and display the records table."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_claim()

    page = ClaimPage(logged_in_driver)
    page.go_to_employee_claims()
    assert page.is_records_table_visible(), "Employee Claims records table not visible"