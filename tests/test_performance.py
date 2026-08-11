from __future__ import annotations

import uuid

import pytest

from pages.dashboard_page import DashboardPage

from pages.performance_page import PerformancePage

def test_performance_employee_trackers_shows_table(logged_in_driver):
    """FR-PERF-01: Employee Trackers page must load with a records table when opened from Performance."""
    dashboard = DashboardPage(logged_in_driver)
    dashboard.action_go_to_performance()

    perf = PerformancePage(logged_in_driver)
    assert perf.is_performance_loaded(), "Performance page did not load"

    try:
        perf.open_employee_trackers()
    except Exception:
        pass

    assert perf.is_employee_trackers_table_visible(), "Employee Trackers table not visible"

def test_kpi_page_loads_and_has_table(logged_in_driver):
    """FR-PERF-02: KPIs configuration page must load and display the KPI list table."""
    perf = PerformancePage(logged_in_driver)
    perf.go_to_kpi_page()
    assert perf.is_kpi_table_visible(), "KPI table not visible on KPI page"