
from datetime import datetime, timedelta
from time import perf_counter

from sqlalchemy import bindparam, text

from db_connection import engine


PIPELINE_NAME = "Employee Incremental ETL"

# Re-read a small portion of the previous window.
# This helps with second-precision employee timestamps.
LOOKBACK_SECONDS = 2

# Do not process timestamps at the current clock boundary.
SETTLE_SECONDS = 2


def find_changed_employee_ids(
    conn,
    checkpoint,
    upper_bound,
):
    """Find employees changed within the processing window."""

    lower_bound = (
        checkpoint - timedelta(seconds=LOOKBACK_SECONDS)
        if checkpoint is not None
        else None
    )

    query = text("""
        SELECT DISTINCT e.employee_id
        FROM employees e
        LEFT JOIN salaries s
            ON e.employee_id = s.employee_id
        WHERE
            (
                :lower_bound IS NULL
                OR (
                    e.last_updated >= :lower_bound
                    AND e.last_updated < :upper_bound
                )
                OR (
                    s.last_updated >= :lower_bound
                    AND s.last_updated < :upper_bound
                )
            )
            AND (
                :lower_bound IS NOT NULL
                OR (
                    e.last_updated < :upper_bound
                    OR s.last_updated < :upper_bound
                )
            )
        ORDER BY e.employee_id
    """)

    return conn.execute(
        query,
        {
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        },
    ).scalars().all()


def get_employee_details(conn, employee_ids):
    """Read analytics-ready records for changed employees."""

    if not employee_ids:
        return []

    query = text("""
        SELECT
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name)
                AS employee_name,
            e.job_title,
            d.department_name,
            d.location,
            s.salary_amount,
            COALESCE(s.bonus, 0) AS bonus,
            s.salary_amount + COALESCE(s.bonus, 0)
                AS total_compensation
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        JOIN salaries s
            ON e.employee_id = s.employee_id
        WHERE e.employee_id IN :employee_ids
        ORDER BY e.employee_id
    """).bindparams(
        bindparam("employee_ids", expanding=True)
    )

    return conn.execute(
        query,
        {"employee_ids": employee_ids},
    ).mappings().all()


def upsert_analytics(conn, rows):
    """Insert new analytics records or update existing ones."""

    if not rows:
        return 0

    query = text("""
        INSERT INTO employee_salary_analytics (
            employee_id,
            employee_name,
            job_title,
            department_name,
            location,
            salary_amount,
            bonus,
            total_compensation
        )
        VALUES (
            :employee_id,
            :employee_name,
            :job_title,
            :department_name,
            :location,
            :salary_amount,
            :bonus,
            :total_compensation
        )
        ON DUPLICATE KEY UPDATE
            employee_name = VALUES(employee_name),
            job_title = VALUES(job_title),
            department_name = VALUES(department_name),
            location = VALUES(location),
            salary_amount = VALUES(salary_amount),
            bonus = VALUES(bonus),
            total_compensation = VALUES(total_compensation)
    """)

    conn.execute(query, [dict(row) for row in rows])

    return len(rows)


def log_run(
    status,
    start_time,
    end_time,
    extracted,
    loaded,
    duration,
    error_message=None,
):
    """Save execution history independently of the ETL transaction."""

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO etl_pipeline_runs (
                    pipeline_name,
                    start_time,
                    end_time,
                    status,
                    extracted_records,
                    loaded_records,
                    execution_seconds,
                    error_message
                )
                VALUES (
                    :pipeline_name,
                    :start_time,
                    :end_time,
                    :status,
                    :extracted,
                    :loaded,
                    :duration,
                    :error_message
                )
            """),
            {
                "pipeline_name": PIPELINE_NAME,
                "start_time": start_time,
                "end_time": end_time,
                "status": status,
                "extracted": extracted,
                "loaded": loaded,
                "duration": round(duration, 3),
                "error_message": error_message,
            },
        )


def run_incremental_load():
    start_time = datetime.now()
    start_clock = perf_counter()

    extracted = 0
    loaded = 0
    upper_bound = None

    print("\nStarting Incremental ETL...")

    try:
        with engine.begin() as conn:

            # Ensure the checkpoint row exists.
            conn.execute(
                text("""
                    INSERT INTO etl_checkpoints (
                        pipeline_name,
                        last_processed_timestamp
                    )
                    VALUES (:name, NULL)
                    ON DUPLICATE KEY UPDATE
                        pipeline_name = pipeline_name
                """),
                {"name": PIPELINE_NAME},
            )

            # Serialize runs of this pipeline.
            checkpoint = conn.execute(
                text("""
                    SELECT last_processed_timestamp
                    FROM etl_checkpoints
                    WHERE pipeline_name = :name
                    FOR UPDATE
                """),
                {"name": PIPELINE_NAME},
            ).scalar_one_or_none()

            print("Previous checkpoint:", checkpoint)

            # Use database time, not the Mac's clock.
            upper_bound = conn.execute(
                text("""
                    SELECT CURRENT_TIMESTAMP(6)
                           - INTERVAL :seconds SECOND
                """),
                {"seconds": SETTLE_SECONDS},
            ).scalar_one()

            # Never move backward if the clock or checkpoint
            # is ahead of the proposed processing boundary.
            if checkpoint is not None and upper_bound <= checkpoint:
                print("No new processing window available.")
                upper_bound = checkpoint

            else:
                employee_ids = find_changed_employee_ids(
                    conn,
                    checkpoint,
                    upper_bound,
                )

                extracted = len(employee_ids)
                print("Changed employees:", extracted)

                rows = get_employee_details(
                    conn,
                    employee_ids,
                )

                # Current project assumes one salary row
                # and one valid department per employee.
                if len(rows) != extracted:
                    raise ValueError(
                        "Employee detail count mismatch. "
                        "Check missing or duplicate salary "
                        "and department records."
                    )

                loaded = upsert_analytics(conn, rows)

                # Checkpoint and analytics changes commit
                # together, or roll back together.
                conn.execute(
                    text("""
                        UPDATE etl_checkpoints
                        SET last_processed_timestamp = :checkpoint
                        WHERE pipeline_name = :name
                          AND (
                              last_processed_timestamp IS NULL
                              OR last_processed_timestamp < :checkpoint
                          )
                    """),
                    {
                        "name": PIPELINE_NAME,
                        "checkpoint": upper_bound,
                    },
                )

        end_time = datetime.now()
        duration = perf_counter() - start_clock

        log_run(
            status="SUCCESS",
            start_time=start_time,
            end_time=end_time,
            extracted=extracted,
            loaded=loaded,
            duration=duration,
        )

        print("Records extracted:", extracted)
        print("Records loaded:", loaded)
        print("Checkpoint:", upper_bound)
        print("Incremental ETL completed successfully!")

    except Exception as error:
        end_time = datetime.now()
        duration = perf_counter() - start_clock

        try:
            log_run(
                status="FAILED",
                start_time=start_time,
                end_time=end_time,
                extracted=extracted,
                loaded=0,
                duration=duration,
                error_message=str(error)[:5000],
            )
        except Exception as logging_error:
            print("Failed to save error log:", logging_error)

        print("Incremental ETL failed:", error)
        raise


if __name__ == "__main__":
    run_incremental_load()
