
from datetime import datetime
from time import perf_counter

from sqlalchemy import text, bindparam

from db_connection import engine


PIPELINE_NAME = "Employee Incremental ETL"


def log_run(
    status,
    start_time,
    end_time,
    extracted,
    loaded,
    duration,
    error_message=None,
):
    """Save ETL execution history in a separate transaction."""

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
    checkpoint = None

    print("\nStarting Incremental ETL...")

    try:
        with engine.begin() as conn:

            # Ensure a checkpoint row exists so it can be locked.
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

            # Lock the checkpoint to serialize pipeline runs.
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

            # Use a fixed database timestamp as the upper bound.
            upper_bound = conn.execute(
                text("SELECT CURRENT_TIMESTAMP(6)")
            ).scalar_one()

            # Detect employee or salary changes.
            changed_query = text("""
                SELECT DISTINCT e.employee_id
                FROM employees e
                LEFT JOIN salaries s
                    ON e.employee_id = s.employee_id
                WHERE (
                    :checkpoint IS NULL
                    OR e.last_updated >= :checkpoint
                    OR s.last_updated >= :checkpoint
                )
                AND (
                    e.last_updated < :upper_bound
                    OR s.last_updated < :upper_bound
                )
                ORDER BY e.employee_id
            """)

            employee_ids = conn.execute(
                changed_query,
                {
                    "checkpoint": checkpoint,
                    "upper_bound": upper_bound,
                },
            ).scalars().all()

            extracted = len(employee_ids)
            print("Changed employees:", extracted)

            if employee_ids:

                details_query = text("""
                    SELECT
                        e.employee_id,
                        CONCAT(
                            e.first_name, ' ', e.last_name
                        ) AS employee_name,
                        e.job_title,
                        d.department_name,
                        d.location,
                        s.salary_amount,
                        COALESCE(s.bonus, 0) AS bonus,
                        s.salary_amount +
                            COALESCE(s.bonus, 0)
                            AS total_compensation
                    FROM employees e
                    JOIN departments d
                        ON e.department_id = d.department_id
                    JOIN salaries s
                        ON e.employee_id = s.employee_id
                    WHERE e.employee_id IN :employee_ids
                """).bindparams(
                    bindparam("employee_ids", expanding=True)
                )

                rows = conn.execute(
                    details_query,
                    {"employee_ids": employee_ids},
                ).mappings().all()

                if len(rows) != extracted:
                    raise ValueError(
                        "Employee detail count mismatch. "
                        "Check salary and department relationships."
                    )

                upsert_query = text("""
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
                        total_compensation =
                            VALUES(total_compensation)
                """)

                conn.execute(
                    upsert_query,
                    [dict(row) for row in rows],
                )

                loaded = len(rows)

            # Save checkpoint only within successful load transaction.
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

        print("Records loaded:", loaded)
        print("Checkpoint boundary:", upper_bound)
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
