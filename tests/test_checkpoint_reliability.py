
import pytest
from sqlalchemy import (
    create_engine,
    text
)


@pytest.fixture
def database():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE etl_checkpoints (
                pipeline_name TEXT PRIMARY KEY,
                last_processed_timestamp TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE analytics (
                employee_id INTEGER PRIMARY KEY,
                salary_amount INTEGER
                    CHECK (salary_amount >= 0)
            )
        """))

        conn.execute(
            text("""
                INSERT INTO etl_checkpoints
                VALUES (:name, :checkpoint)
            """),
            {
                "name": "Employee Incremental ETL",
                "checkpoint": "2026-10-29 12:00:00"
            }
        )

    yield engine
    engine.dispose()


def get_checkpoint(engine):
    with engine.connect() as conn:
        return conn.execute(
            text("""
                SELECT last_processed_timestamp
                FROM etl_checkpoints
                WHERE pipeline_name =
                    'Employee Incremental ETL'
            """)
        ).scalar_one()


def test_successful_load_advances_checkpoint(database):
    with database.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO analytics
                VALUES (101, 125000)
            """)
        )

        conn.execute(
            text("""
                UPDATE etl_checkpoints
                SET last_processed_timestamp =
                    '2026-10-29 13:00:00'
            """)
        )

    assert get_checkpoint(database) == (
        "2026-10-29 13:00:00"
    )


def test_failed_load_rolls_back_checkpoint(database):
    original_checkpoint = get_checkpoint(database)

    with pytest.raises(Exception):
        with database.begin() as conn:
            conn.execute(
                text("""
                    UPDATE etl_checkpoints
                    SET last_processed_timestamp =
                        '2026-10-29 14:00:00'
                """)
            )

            # Negative salary violates the CHECK constraint.
            conn.execute(
                text("""
                    INSERT INTO analytics
                    VALUES (101, -5000)
                """)
            )

    assert get_checkpoint(database) == original_checkpoint

    with database.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM analytics")
        ).scalar_one()

    assert count == 0


def test_duplicate_employee_rejected(database):
    with database.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO analytics
                VALUES (101, 125000)
            """)
        )

    with pytest.raises(Exception):
        with database.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO analytics
                    VALUES (101, 130000)
                """)
            )

    with database.connect() as conn:
        count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM analytics
                WHERE employee_id = 101
            """)
        ).scalar_one()

    assert count == 1
