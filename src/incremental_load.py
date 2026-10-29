
from datetime import datetime, timezone
from sqlalchemy import text, bindparam
from db_connection import engine

PIPELINE_NAME = "Employee Incremental ETL"


def run_incremental_load():
    print("\nStarting Incremental ETL Load...")

    with engine.begin() as conn:

        # STEP 1: Read checkpoint and lock it
        checkpoint = conn.execute(
            text("""
                SELECT last_processed_timestamp
                FROM etl_checkpoints
                WHERE pipeline_name = :name
                FOR UPDATE
            """),
            {"name": PIPELINE_NAME}
        ).scalar_one_or_none()

        if checkpoint is None:
            print("No checkpoint found. Initial load.")
        else:
            print("Last checkpoint:", checkpoint)

        # STEP 2: Capture an upper time boundary
        upper_bound = conn.execute(
            text("SELECT CURRENT_TIMESTAMP(6)")
        ).scalar_one()

        # STEP 3: Detect changed employees
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
                "upper_bound": upper_bound
            }
        ).scalars().all()

        print("Changed employees:", len(employee_ids))

        # STEP 4: Read current employee details
        rows = []

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
                {"employee_ids": employee_ids}
            ).mappings().all()

            if len(rows) != len(employee_ids):
                raise ValueError(
                    "Some employees are missing salary "
                    "or department information."
                )

            # STEP 5: Insert or update analytics
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
                [dict(row) for row in rows]
            )

            for row in rows:
                print(
                    "Loaded employee:",
                    row["employee_id"],
                    "| Salary:",
                    row["salary_amount"]
                )

        # STEP 6: Advance checkpoint
        # This is committed with the analytics updates.
        conn.execute(
            text("""
                INSERT INTO etl_checkpoints (
                    pipeline_name,
                    last_processed_timestamp
                )
                VALUES (:name, :checkpoint)
                ON DUPLICATE KEY UPDATE
                    last_processed_timestamp =
                        GREATEST(
                            COALESCE(
                                last_processed_timestamp,
                                VALUES(last_processed_timestamp)
                            ),
                            VALUES(last_processed_timestamp)
                        )
            """),
            {
                "name": PIPELINE_NAME,
                "checkpoint": upper_bound
            }
        )

    print("\nIncremental ETL completed!")
    print("Records loaded:", len(rows))
    print("Checkpoint updated:", upper_bound)


if __name__ == "__main__":
    run_incremental_load()
