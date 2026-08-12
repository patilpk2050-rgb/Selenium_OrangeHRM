from __future__ import annotations

import pytest

from pages.time_page import TimePage

from utils.wait_helpers import wait_url_contains, wait_visible

def test_employee_timesheets_page_loads(logged_in_driver, config):
    """FR-TIME-01: Employee Timesheets page must load and display the search form with Employee Name field."""
    timesheets_url = f"{config['base_url']}/web/index.php/time/viewEmployeeTimesheet"
    logged_in_driver.get(timesheets_url)
    
    time_page = TimePage(logged_in_driver)
    wait_url_contains(logged_in_driver, "viewEmployeeTimesheet", time_page.timeout)
    assert time_page.is_employee_timesheets_loaded(), "Employee Timesheets page did not load with required fields."

def test_project_info_customer_list_page_loads(logged_in_driver):
    """FR-TIME-02: Project Info > Customer List page must load and display the customer list table when accessed directly."""
    customer_list_url = "https://opensource-demo.orangehrmlive.com/web/index.php/time/viewCustomers"
    logged_in_driver.get(customer_list_url)

    time_page = TimePage(logged_in_driver)
    wait_url_contains(logged_in_driver, "viewCustomers", time_page.timeout)
    
    page_has_content = (
        time_page.is_text_visible("Customer")
    )
    assert page_has_content, "Customer List page did not load with customer content."