# OrangeHRM UI Automation Framework

## Overview

Selenium HR Test Framework is a scalable UI test automation framework built using Python, Selenium WebDriver, Pytest and the Page Object Model (POM) design pattern. The framework automates key workflows of the OrangeHRM application and is designed for maintainability, reusability and CI/CD integration.

This project demonstrates automation framework practices including:
- Page Object Model (POM)
- Data-driven testing
- Pytest fixtures
- Configurable test execution
- HTML reporting
- Screenshot capture on failures
- Cross-browser execution support
- Modular and maintainable architecture

---

## Technology Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python 3.x |
| Automation Tool | Selenium WebDriver |
| Test Framework | Pytest |
| Design Pattern | Page Object Model (POM) |
| Reporting | Pytest HTML |
| Test Data | JSON |
| Version Control | Git & GitHub |
| CI/CD Ready | GitHub Actions / Jenkins |

---

## Framework Features

- Page Object Model architecture
- Reusable page classes and utilities
- Centralized configuration management
- JSON-based test data management
- Screenshot capture for failed tests
- Detailed HTML execution reports
- Pytest markers for test categorization
- Easy maintenance and scalability
- CI/CD integration ready

---

## Project Structure

```text
selenium-hr-test-framework/
│
├── pages/                 # Page Object classes
├── tests/                 # Test cases
├── utils/                 # Utility functions
├── data/                  # Test data files
├── reports/               # Generated execution reports
├── pytest.ini             # Pytest configuration
├── requirements.txt       # Project dependencies
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/babadxxk/selenium-hr-test-framework.git
cd selenium-hr-test-framework
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows:

```bash
(source\) .venv\Scripts\Activate.ps1
```

Linux/Mac:

```bash
(source/) .venv/Scripts/Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Execute Tests

### Run Complete Test Suite

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_login.py -v
```

### Run Smoke Tests

```bash
pytest -m smoke
```

### Run Authentication Tests

```bash
pytest -m auth
```

### Generate HTML Report

```bash
pytest --html=reports/report.html --self-contained-html
```

---

## Reporting

After execution, reports are generated in the reports directory.

Features:
- Pass/Fail summary
- Execution duration
- Failure screenshots
- Detailed test logs

---

## Test Data Management

Test data is maintained in JSON format to support data-driven testing.

Example:

```json
{
  "username": "Admin",
  "password": "admin123"
}
```

---

## Design Principles

The framework follows:

- Page Object Model (POM)
- Reusable utility methods
- Separation of test logic and page logic
- Scalable automation architecture

---

## CI/CD Integration

Typical pipeline steps:

1. Install dependencies
2. Execute tests
3. Generate reports
4. Publish results