
import pandas as pd
from pathlib import Path
from db_connection import engine

# Find the project's data folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Tables to extract from MySQL
TABLES = [
    "employees",
    "departments",
    "salaries",
    "projects",
    "employee_projects",
    "attendance"
]

def extract_data():
    print("Starting Employee Management Data Extraction...")

    extracted_data = {}

    with engine.connect() as connection:
        for table in TABLES:

            # Extract records from MySQL
            query = f"SELECT * FROM `{table}`"

            df = pd.read_sql(query, connection)

            # Store DataFrame in memory
            extracted_data[table] = df

            # Save extracted data as CSV
            output_file = DATA_DIR / f"{table}.csv"
            df.to_csv(output_file, index=False)

            print(
                f"Extracted {len(df)} records "
                f"from {table}"
            )

    print("Data Extraction Completed Successfully!")

    return extracted_data


if __name__ == "__main__":
    extract_data()
