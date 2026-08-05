from __future__ import annotations

import pytest

from pages.admin_page import AdminPage

from pages.dashboard_page import DashboardPage

def test_system_users_page_loads_and_shows_user_list(logged_in_driver):
    """FR-ADM-01: System Users page must load and display the user list table."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_admin()

    admin = AdminPage(logged_in_driver)
    # Verify the Admin dashboard redirects to System Users and shows the user table
    assert admin.is_system_users_loaded(), "System Users page did not load successfully."
    rows = admin.get_table_row_texts()
    assert rows, "Expected user list rows on System Users page."

def test_add_user_form_loads_with_required_fields(logged_in_driver):
    """FR-ADM-02: Add User form must load when the Add button is clicked; User Role, Employee Name, Status, Username and Password fields must be present."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_admin()

    admin = AdminPage(logged_in_driver)
    # Open the Add User form and confirm required form fields are visible
    admin.open_add_user_form()

    assert admin.is_add_user_form_loaded(), "Add User form did not show all required fields."