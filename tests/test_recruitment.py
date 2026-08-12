from __future__ import annotations

import pytest

import time as time_module

from pages.dashboard_page import DashboardPage

from pages.recruitment_page import RecruitmentPage

def test_candidates_page_loads_and_shows_columns(logged_in_driver):
    """FR-REC-01: Candidates page must load and display the candidate list table with required columns."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_recruitment()

    rec = RecruitmentPage(logged_in_driver)
    time_module.sleep(1)
    assert rec.is_candidates_page_loaded(), "Candidates page did not load with required elements."

def test_add_candidate_invalid_email_shows_error(logged_in_driver):
    """FR-REC-02: Submitting the Add Candidate form with an invalid email must show an email validation error."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_recruitment()

    rec = RecruitmentPage(logged_in_driver)
    rec.open_add_candidate_form()
    time_module.sleep(1)

    assert rec.is_add_candidate_form_loaded(), "Add Candidate form did not load with required fields."

    rec.submit_add_candidate_form(first_name='Invalid', last_name='Email', email='abc@xyz')
    time_module.sleep(1)

    messages = rec.get_add_candidate_validation_messages()
    assert messages, f"Expected validation messages for invalid email, got {messages}"
    assert any('email' in m.lower() or 'valid' in m.lower() or '@' in m for m in messages), (
        f"Expected email validation messages, got {messages}"
    )