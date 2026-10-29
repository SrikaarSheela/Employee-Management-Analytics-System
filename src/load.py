
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = BASE_DIR / "reports" / "employee_salary_analytics.csv"


def load_employee_analytics():

    print("Starting Employee Analytics Data Load...")

    # 1. Read transformed CSV
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            "Transformed CSV not found. Run transform.py first."
        )

    df = pd.read_csv(REPORT_FILE)

    # 2. Validate before loading
    if df.empty:
        raise ValueError("No records available to load.")

    if df["employee_id"].duplicated().any():
        raise ValueError("Duplicate employee IDs detected.")

    if df.isna().any().any():
        raise ValueError("Null values detected in reporting data.")

    print("Records ready to load:", len(df))

    # 3. Upsert records into MySQL
    upsert_sql = text("""
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

    records = df.to_dict(orient="records")

    # 4. Load and validate in one transaction
    with engine.begin() as connection:

        connection.execute(upsert_sql, records)

        result = connection.execute(text("""
            SELECT
                COUNT(*) AS employee_count,
                SUM(salary_amount) AS total_salary,
                SUM(total_compensation) AS total_compensation
            FROM employee_salary_analytics
        """)).mappings().one()

        # 5. Validate the database against the CSV
        expected_ids = set(df["employee_id"].tolist())

        loaded_ids = set(
            connection.execute(
                text(
                    "SELECT employee_id "
                    "FROM employee_salary_analytics"
                )
            ).scalars().all()
        )

        if expected_ids != loaded_ids:
            raise ValueError(
                "Employee IDs do not match the transformed CSV."
            )

        if result["employee_count"] != len(df):
            raise ValueError("Employee count mismatch.")

        expected_salary = round(float(df["salary_amount"].sum()), 2)
        actual_salary = round(float(result["total_salary"]), 2)

        expected_comp = round(
            float(df["total_compensation"].sum()), 2
        )
        actual_comp = round(
            float(result["total_compensation"]), 2
        )

        if expected_salary != actual_salary:
            raise ValueError("Salary total mismatch.")

        if expected_comp != actual_comp:
            raise ValueError("Compensation total mismatch.")

    print("Data loaded successfully!")
    print("Validated employee count:", result["employee_count"])
    print("Validated annual salary:", actual_salary)
    print("Validated total compensation:", actual_comp)


if __name__ == "__main__":
    load_employee_analytics()
