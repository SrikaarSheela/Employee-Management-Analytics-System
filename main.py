
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import text

# ==========================================
# PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR / "src"))

from db_connection import engine
from extract import extract_data
from transform import transform_employee_data
from load import load_employee_analytics

# ==========================================
# LOGGING CONFIGURATION
# ==========================================

logging.basicConfig(
    filename=LOG_DIR / "etl_pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# UTC TIME FUNCTION
# ==========================================

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ==========================================
# START PIPELINE EXECUTION
# ==========================================

def start_run():
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO etl_pipeline_runs
                    (pipeline_name, start_time, status)
                VALUES
                    (:name, :started, 'RUNNING')
            """),
            {
                "name": "Employee Management ETL",
                "started": utc_now()
            }
        )

        return result.lastrowid


# ==========================================
# UPDATE PIPELINE EXECUTION STATUS
# ==========================================

def finish_run(
    run_id,
    status,
    extracted,
    loaded,
    duration,
    error_message=None
):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE etl_pipeline_runs
                SET
                    end_time = :ended,
                    status = :status,
                    extracted_records = :extracted,
                    loaded_records = :loaded,
                    execution_seconds = :duration,
                    error_message = :error
                WHERE run_id = :run_id
            """),
            {
                "ended": utc_now(),
                "status": status,
                "extracted": extracted,
                "loaded": loaded,
                "duration": duration,
                "error": error_message,
                "run_id": run_id
            }
        )


# ==========================================
# MAIN ETL PIPELINE
# ==========================================

def run_pipeline():

    start_time = datetime.now()
    extracted_count = 0
    loaded_count = 0

    run_id = start_run()

    print("=" * 50)
    print("EMPLOYEE MANAGEMENT ETL PIPELINE")
    print("Run ID:", run_id)
    print("=" * 50)

    logging.info("Pipeline run %s started", run_id)

    try:

        # ==================================
        # STEP 1: EXTRACT
        # ==================================

        print("\nSTEP 1: EXTRACT")

        extracted_data = extract_data()

        extracted_count = sum(
            len(df) for df in extracted_data.values()
        )

        logging.info(
            "Extracted %s records",
            extracted_count
        )

        print(
            "Total extracted records:",
            extracted_count
        )

        # ==================================
        # STEP 2: TRANSFORM
        # ==================================

        print("\nSTEP 2: TRANSFORM")

        transformed_data = transform_employee_data()

        print(
            "Total transformed employees:",
            len(transformed_data)
        )

        logging.info(
            "Transformed %s employee records",
            len(transformed_data)
        )

        # ==================================
        # STEP 3: LOAD
        # ==================================

        print("\nSTEP 3: LOAD")

        load_employee_analytics()

        logging.info("Data load completed")

        # ==================================
        # STEP 4: AUTOMATED TESTING
        # ==================================

        print("\nSTEP 4: AUTOMATED TESTING")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(BASE_DIR / "tests"),
                "-v"
            ],
            cwd=BASE_DIR,
            check=True
        )

        logging.info("Automated tests passed")

        # ==================================
        # STEP 5: VALIDATE LOADED RECORDS
        # ==================================

        print("\nSTEP 5: VALIDATE LOADED RECORDS")

        with engine.connect() as conn:
            loaded_count = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM employee_salary_analytics
                """)
            ).scalar_one()

        if loaded_count != len(transformed_data):
            raise ValueError(
                "Loaded record count does not match "
                "transformed record count."
            )

        print(
            "Validated analytics records:",
            loaded_count
        )

        logging.info(
            "Validated %s analytics records",
            loaded_count
        )

        # ==================================
        # STEP 6: COMPLETE PIPELINE
        # ==================================

        duration = (
            datetime.now() - start_time
        ).total_seconds()

        finish_run(
            run_id,
            "SUCCESS",
            extracted_count,
            loaded_count,
            duration
        )

        logging.info(
            "Pipeline run %s completed successfully",
            run_id
        )

        print("\n" + "=" * 50)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        print("Run ID:", run_id)
        print("Extracted records:", extracted_count)
        print("Transformed records:", len(transformed_data))
        print("Loaded analytics records:", loaded_count)
        print("Automated tests: PASSED")
        print(f"Execution time: {duration:.3f} seconds")

    # ======================================
    # ERROR HANDLING
    # ======================================

    except Exception as error:

        duration = (
            datetime.now() - start_time
        ).total_seconds()

        logging.exception(
            "Pipeline run %s failed",
            run_id
        )

        try:
            finish_run(
                run_id,
                "FAILED",
                extracted_count,
                loaded_count,
                duration,
                str(error)
            )

        except Exception:
            logging.exception(
                "Could not update failed run %s",
                run_id
            )

        print("\n" + "=" * 50)
        print("ETL PIPELINE FAILED!")
        print("=" * 50)

        print("Run ID:", run_id)
        print("Error:", error)

        raise


# ==========================================
# PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    run_pipeline()
