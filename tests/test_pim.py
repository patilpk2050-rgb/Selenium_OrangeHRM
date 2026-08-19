from __future__ import annotations

import pytest

from selenium.webdriver.common.by import By

from pages.dashboard_page import DashboardPage

from pages.pim_page import PIMPage

import time


@pytest.mark.pim
@pytest.mark.regression
@pytest.mark.smoke
def test_employee_list_loads_and_has_records(logged_in_driver):
    """FR-PIM-01: Employee List page must load and have at least one record."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_pim()

    pim = PIMPage(logged_in_driver)
    assert pim.is_employee_list_loaded(), "PIM Employee List did not load or no rows present."


@pytest.mark.pim
@pytest.mark.regression
def test_add_employee_and_verify_search(logged_in_driver):
    """FR-PIM-02: A new employee must be successfully added through the Add Employee form and appear in PIM search results."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_pim()
    pim = PIMPage(logged_in_driver)

    pim.add_employee("Baba", "", "Dook", "1069")

    emp_id = pim.get_current_employee_id()
    assert emp_id, "Could not read employee id after saving the new employee"

    import time

    found = False
    for attempt in range(1, 4):
        time.sleep(1 * attempt)
        dashboard.action_go_to_pim()
        try:
            pim.search_by_employee_id(emp_id)
        except Exception:
            continue

        rows = pim.get_table_row_texts()
        if any(emp_id in r for r in rows):
            found = True
            break

    assert found, f"Added employee ID {emp_id} not found in search results after retries: {rows if 'rows' in locals() else []}"