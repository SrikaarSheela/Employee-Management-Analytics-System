
from datetime import datetime, timezone
from sqlalchemy import text
from db_connection import engine

PIPELINE_NAME = "Employee Incremental ETL"


def extract_incremental_employees():
    print("Starting Incremental Employee Extraction...")

    with engine.connect() as conn:
        checkpoint = conn.execute(
            text("""
                SELECT last_processed_timestamp
                FROM etl_checkpoints
                WHERE pipeline_name = :pipeline_name
            """),
            {"pipeline_name": PIPELINE_NAME}
        ).scalar_one_or_none()

        if checkpoint is None:
            print("No checkpoint found. Running initial extraction.")
        else:
            print("Last successful checkpoint:", checkpoint)

        # Detect employee or salary changes
        query = text("""
            SELECT
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.age,
                e.department_id,
                e.hire_date,
                e.job_title,
                e.last_updated AS employee_updated,
                s.salary_amount,
                s.bonus,
                s.last_updated AS salary_updated
            FROM employees e
            LEFT JOIN salaries s
                ON e.employee_id = s.employee_id
            WHERE :checkpoint IS NULL
               OR e.last_updated >= :checkpoint
               OR s.last_updated >= :checkpoint
            ORDER BY e.employee_id
        """)

        result = conn.execute(
            query,
            {"checkpoint": checkpoint}
        )

        employees = result.mappings().all()

    print("Records extracted:", len(employees))

    for employee in employees:
        print(
            "Employee ID:", employee["employee_id"],
            "| Name:", employee["first_name"],
            employee["last_name"],
            "| Salary:", employee["salary_amount"],
            "| Bonus:", employee["bonus"]
        )

    return employees


if __name__ == "__main__":
    extract_incremental_employees()
