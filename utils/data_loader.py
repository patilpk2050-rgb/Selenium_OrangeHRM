from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

"""Helpers to load test data files (JSON, CSV) from the project data folder."""

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_json(relative_path: str) -> dict[str, Any]:
    data_path = PROJECT_ROOT / relative_path
    with data_path.open(encoding="utf-8") as file:
        return json.load(file)

def load_csv(relative_path: str) -> list[dict[str, Any]]:
    data_path = PROJECT_ROOT / relative_path
    with data_path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)