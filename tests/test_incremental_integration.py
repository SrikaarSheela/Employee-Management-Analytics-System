
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from incremental_load import run_incremental_load


def get_test_engine():
    """Create a database connection from environment settings."""
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")

    url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "company_db"),
    )

    return create_engine(url)


@pytest.fixture(scope="module")
def db_engine():
    engine = get_test_engine()

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"MySQL unavailable: {type(exc).__name__}")

    yield engine
    engine.dispose()


def test_analytics_has_no_duplicate_ids(db_engine):
    with db_engine.connect() as conn:
        duplicates = conn.execute(text("""
            SELECT employee_id, COUNT(*) AS total
            FROM employee_salary_analytics
            GROUP BY employee_id
            HAVING COUNT(*) > 1
        """)).all()

    assert duplicates == []


def test_analytics_compensation_matches_source(db_engine):
    with db_engine.connect() as conn:
        mismatches = conn.execute(text("""
            SELECT s.employee_id
            FROM salaries s
            JOIN employee_salary_analytics a
                ON s.employee_id = a.employee_id
            WHERE NOT (
                s.salary_amount <=> a.salary_amount
                AND
                (s.salary_amount + COALESCE(s.bonus, 0))
                    <=> a.total_compensation
            )
        """)).all()

    assert mismatches == []


def test_checkpoint_exists(db_engine):
    with db_engine.connect() as conn:
        checkpoint = conn.execute(
            text("""
                SELECT last_processed_timestamp
                FROM etl_checkpoints
                WHERE pipeline_name = :name
            """),
            {"name": "Employee Incremental ETL"}
        ).scalar_one_or_none()

    assert checkpoint is not None

