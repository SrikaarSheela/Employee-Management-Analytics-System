
import sys
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from incremental_load import find_changed_employee_ids


@pytest.fixture
def database():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE employees (
                employee_id INTEGER PRIMARY KEY,
                last_updated DATETIME
            )
        """))

        conn.execute(text("""
            CREATE TABLE salaries (
                salary_id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                last_updated DATETIME
            )
        """))

    yield engine
    engine.dispose()


def add_employee(engine, employee_id, employee_time, salary_time):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO employees (
                    employee_id, last_updated
                )
                VALUES (:id, :updated)
            """),
            {
                "id": employee_id,
                "updated": employee_time,
            },
        )

        conn.execute(
            text("""
                INSERT INTO salaries (
                    salary_id, employee_id, last_updated
                )
                VALUES (:id, :id, :updated)
            """),
            {
                "id": employee_id,
                "updated": salary_time,
            },
        )


CHECKPOINT = datetime(2026, 10, 30, 10, 0, 0)
UPPER_BOUND = datetime(2026, 10, 30, 11, 0, 0)


def detect(engine, checkpoint=CHECKPOINT, upper=UPPER_BOUND):
    with engine.connect() as conn:
        return find_changed_employee_ids(
            conn, checkpoint, upper
        )


def test_employee_update_detected(database):
    add_employee(
        database,
        101,
        datetime(2026, 10, 30, 10, 30),
        datetime(2026, 10, 29, 9, 0),
    )

    assert detect(database) == [101]


def test_salary_only_update_detected(database):
    add_employee(
        database,
        102,
        datetime(2026, 10, 29, 9, 0),
        datetime(2026, 10, 30, 10, 45),
    )

    assert detect(database) == [102]


def test_future_change_not_selected(database):
    add_employee(
        database,
        103,
        datetime(2026, 10, 29, 9, 0),
        datetime(2026, 10, 30, 11, 30),
    )

    assert detect(database) == []


def test_old_record_skipped(database):
    add_employee(
        database,
        104,
        datetime(2026, 10, 29, 9, 0),
        datetime(2026, 10, 29, 10, 0),
    )

    assert detect(database) == []


def test_timestamp_overlap_detected(database):
    add_employee(
        database,
        105,
        datetime(2026, 10, 30, 9, 59, 59),
        datetime(2026, 10, 29, 9, 0),
    )

    assert detect(database) == [105]


def test_upper_boundary_excluded(database):
    add_employee(
        database,
        106,
        datetime(2026, 10, 30, 11, 0, 0),
        datetime(2026, 10, 29, 9, 0),
    )

    assert detect(database) == []


def test_initial_load(database):
    add_employee(
        database,
        107,
        datetime(2026, 10, 29, 9, 0),
        datetime(2026, 10, 29, 9, 0),
    )

    assert detect(database, checkpoint=None) == [107]
