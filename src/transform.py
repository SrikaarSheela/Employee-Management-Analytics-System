
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def transform_employee_data():

    print("Starting Employee Data Transformation...")

    # Step 1: Read extracted CSV files
    employees = pd.read_csv(DATA_DIR / "employees.csv")
    departments = pd.read_csv(DATA_DIR / "departments.csv")
    salaries = pd.read_csv(DATA_DIR / "salaries.csv")

    print("CSV files loaded successfully.")

    # Step 2: Validate employee IDs
    if employees["employee_id"].duplicated().any():
        raise ValueError("Duplicate employee IDs detected.")

    if employees["employee_id"].isna().any():
        raise ValueError("Missing employee IDs detected.")

    # Step 3: Select the latest salary per employee
    salaries["effective_date"] = pd.to_datetime(
        salaries["effective_date"],
        errors="raise"
    )

    salaries = (
        salaries.sort_values(
            ["effective_date", "salary_id"]
        )
        .drop_duplicates(
            subset=["employee_id"],
            keep="last"
        )
    )

    # Step 4: Join employee and department data
    employee_data = employees.merge(
        departments[
            ["department_id", "department_name", "location"]
        ],
        on="department_id",
        how="left",
        validate="many_to_one"
    )

    # Step 5: Join salary information
    employee_data = employee_data.merge(
        salaries[
            ["employee_id", "salary_amount", "bonus"]
        ],
        on="employee_id",
        how="left",
        validate="one_to_one"
    )

    # Step 6: Validate important fields
    required_columns = [
        "employee_id",
        "first_name",
        "department_name",
        "salary_amount"
    ]

    if employee_data[required_columns].isna().any().any():
        raise ValueError(
            "Missing required employee, department, or salary data."
        )

    if (employee_data["salary_amount"] < 0).any():
        raise ValueError("Negative salary amount detected.")

    # Step 7: Create employee full name
    employee_data["employee_name"] = (
        employee_data["first_name"].fillna("")
        + " "
        + employee_data["last_name"].fillna("")
    ).str.strip()

    # Step 8: Calculate total compensation
    employee_data["bonus"] = employee_data["bonus"].fillna(0)

    employee_data["total_compensation"] = (
        employee_data["salary_amount"]
        + employee_data["bonus"]
    )

    # Step 9: Select reporting columns
    final_data = employee_data[
        [
            "employee_id",
            "employee_name",
            "job_title",
            "department_name",
            "location",
            "salary_amount",
            "bonus",
            "total_compensation"
        ]
    ].copy()

    # Step 10: Sort by employee ID
    final_data = final_data.sort_values("employee_id")

    # Step 11: Save transformed dataset
    output_file = REPORTS_DIR / "employee_salary_analytics.csv"

    final_data.to_csv(output_file, index=False)

    print("Transformation completed successfully!")
    print("Total employees:", len(final_data))
    print(
        "Total annual salary:",
        final_data["salary_amount"].sum()
    )
    print(
        "Total compensation:",
        final_data["total_compensation"].sum()
    )
    print("Output file:", output_file)

    return final_data


if __name__ == "__main__":
    transform_employee_data()
