
from decimal import Decimal
from datetime import datetime

import pytest


def calculate_total_compensation(salary, bonus):
    """Calculate salary plus bonus."""
    return Decimal(str(salary)) + Decimal(str(bonus or 0))


def find_changed_employees(records, checkpoint):
    """Find records updated at or after the checkpoint."""
    if checkpoint is None:
        return records

    return [
        record
        for record in records
        if (
            record["employee_updated"] >= checkpoint
            or record["salary_updated"] >= checkpoint
        )
    ]


def upsert_employee(store, employee):
    """Simulate an analytics-table upsert."""
    store[employee["employee_id"]] = employee


def test_salary_calculation():
    result = calculate_total_compensation(125000, 10000)
    assert result == Decimal("135000")


def test_null_bonus():
    result = calculate_total_compensation(80000, None)
    assert result == Decimal("80000")


def test_employee_change_detected():
    checkpoint = datetime(2026, 10, 29, 12, 0)

    records = [
        {
            "employee_id": 101,
            "employee_updated": datetime(2026, 10, 29, 13, 0),
            "salary_updated": datetime(2026, 10, 29, 11, 0),
        }
    ]

    changed = find_changed_employees(records, checkpoint)

    assert len(changed) == 1
    assert changed[0]["employee_id"] == 101


def test_salary_change_detected():
    checkpoint = datetime(2026, 10, 29, 12, 0)

    records = [
        {
            "employee_id": 102,
            "employee_updated": datetime(2026, 10, 29, 11, 0),
            "salary_updated": datetime(2026, 10, 29, 13, 0),
        }
    ]

    changed = find_changed_employees(records, checkpoint)

    assert len(changed) == 1


def test_unchanged_employee_skipped():
    checkpoint = datetime(2026, 10, 29, 12, 0)

    records = [
        {
            "employee_id": 103,
            "employee_updated": datetime(2026, 10, 29, 10, 0),
            "salary_updated": datetime(2026, 10, 29, 11, 0),
        }
    ]

    changed = find_changed_employees(records, checkpoint)

    assert changed == []


def test_initial_load():
    records = [
        {
            "employee_id": 101,
            "employee_updated": datetime(2026, 10, 29, 10, 0),
            "salary_updated": datetime(2026, 10, 29, 10, 0),
        }
    ]

    changed = find_changed_employees(records, None)

    assert len(changed) == 1


def test_upsert_prevents_duplicates():
    store = {}

    employee = {
        "employee_id": 101,
        "salary_amount": 120000,
    }

    upsert_employee(store, employee)

    employee["salary_amount"] = 125000
    upsert_employee(store, employee)

    assert len(store) == 1
    assert store[101]["salary_amount"] == 125000


def test_checkpoint_progression():
    old_checkpoint = datetime(2026, 10, 29, 12, 0)
    new_checkpoint = datetime(2026, 10, 29, 13, 0)

    assert new_checkpoint > old_checkpoint
