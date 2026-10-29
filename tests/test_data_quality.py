
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = (
    BASE_DIR / "reports" / "employee_salary_analytics.csv"
)


@pytest.fixture(scope="module")
def employee_data():
    if not REPORT_FILE.exists():
        pytest.fail(
            "Analytics CSV not found. Run python main.py first."
        )

    return pd.read_csv(REPORT_FILE)


def test_employee_ids_are_unique(employee_data):
    assert employee_data["employee_id"].is_unique, (
        "Duplicate employee IDs detected."
    )


def test_employee_ids_are_not_null(employee_data):
    assert employee_data["employee_id"].notna().all(), (
        "Missing employee IDs detected."
    )


def test_required_fields(employee_data):
    required_columns = [
        "employee_id",
        "employee_name",
        "department_name",
        "salary_amount",
        "total_compensation"
    ]

    assert employee_data[required_columns].notna().all().all(), (
        "Missing required values detected."
    )


def test_salary_amounts(employee_data):
    assert (employee_data["salary_amount"] >= 0).all(), (
        "Negative salary amounts detected."
    )


def test_bonus_amounts(employee_data):
    assert (employee_data["bonus"] >= 0).all(), (
        "Negative bonus amounts detected."
    )


def test_total_compensation(employee_data):
    expected = (
        employee_data["salary_amount"]
        + employee_data["bonus"]
    )

    actual = employee_data["total_compensation"]

    assert (
        (expected - actual).abs() < 0.01
    ).all(), "Total compensation calculation mismatch."


def test_department_names(employee_data):
    assert (
        employee_data["department_name"]
        .astype("string")
        .str.strip()
        .fillna("")
        .ne("")
        .all()
    ), "Missing department names detected."


def test_employee_data_not_empty(employee_data):
    assert len(employee_data) > 0, (
        "Employee analytics dataset is empty."
    )


def test_employee_count_matches_source(employee_data):
    source_file = BASE_DIR / "data" / "employees.csv"

    if not source_file.exists():
        pytest.fail("Source employees.csv not found.")

    source = pd.read_csv(source_file)

    assert len(employee_data) == len(source), (
        "Employee count mismatch between source and analytics."
    )


def test_salary_totals(employee_data):
    salary_total = employee_data["salary_amount"].sum()

    compensation_total = (
        employee_data["total_compensation"].sum()
    )

    assert compensation_total >= salary_total, (
        "Total compensation is less than total salary."
    )
