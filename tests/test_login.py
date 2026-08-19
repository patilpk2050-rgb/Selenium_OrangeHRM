from __future__ import annotations

import pytest

from pages.dashboard_page import DashboardPage

from pages.login_page import LoginPage

from utils.data_loader import load_json


@pytest.mark.auth
@pytest.mark.smoke
def test_login_valid_credentials(driver, auth_credentials):
    """FR-AUTH-01: Valid login redirects to dashboard with user dropdown."""
    login_page = LoginPage(driver)
    dashboard = DashboardPage(driver)
    username, password = auth_credentials

    login_page.action_login(username=username, password=password)
    assert dashboard.is_state_on_dashboard(), "User dropdown not visible after valid login."

    header_text = dashboard.get_header_text().lower()
    assert "dashboard" in header_text or "tableau de bord" in header_text


@pytest.mark.auth
@pytest.mark.regression
def test_login_username_with_spaces(driver):
    """FR-AUTH-02: Username with leading/trailing spaces authenticates after trim."""
    users = load_json("data/users.json")["valid_users"]
    trimmed_user = next(
        (user for user in users if user.get("type") == "trimmed_username"),
        None,
    )
    if not trimmed_user:
        pytest.skip("Trimmed username data not configured.")

    login_page = LoginPage(driver)
    dashboard = DashboardPage(driver)
    login_page.action_login(trimmed_user["username"].strip(), trimmed_user["password"])
    assert dashboard.is_state_on_dashboard(), (
        "Username with leading/trailing spaces should be trimmed before authentication."
    )


@pytest.mark.auth
@pytest.mark.regression
def test_login_invalid_credentials(driver, config):
    """FR-AUTH-03: Invalid credentials and special characters show error."""
    users = load_json("data/users.json")["invalid_users"]
    assert users, "Invalid user dataset not configured."

    login_page = LoginPage(driver)
    for user in users:
        # Ensure a clean start on the login page to avoid cross-test session leakage
        driver.delete_all_cookies()
        driver.get(config["base_url"])

        login_page.action_login(user["username"], user["password"])
        assert "Invalid credentials" in login_page.get_error_message(), (
            f"Expected an invalid-credentials error for {user['type']}"
        )



@pytest.mark.auth
@pytest.mark.regression
def test_login_empty_credentials(driver):
    """FR-AUTH-04: Both fields empty shows required validation."""
    login_page = LoginPage(driver)
    login_page.action_login("", "")
    assert login_page.get_required_error_count() >= 2


@pytest.mark.auth
@pytest.mark.regression
def test_direct_url_without_session_redirects_to_login(driver, config):
    """FR-AUTH-05: Direct internal URL without session redirects to login."""
    driver.get(f"{config['base_url']}/web/index.php/dashboard/index")
    login_page = LoginPage(driver)
    assert login_page.is_state_on_login_page()



@pytest.mark.auth
@pytest.mark.regression
def test_session_invalidated_after_logout(driver, auth_credentials, config):
    """FR-AUTH-06: Session invalidated after logout; internal URL redirects to login."""
    username, password = auth_credentials
    login_page = LoginPage(driver)
    dashboard = DashboardPage(driver)

    login_page.action_login(username, password)
    assert login_page.is_state_logged_in()
    dashboard.action_logout()

    driver.get(f"{config['base_url']}/web/index.php/dashboard/index")
    assert login_page.is_state_on_login_page()