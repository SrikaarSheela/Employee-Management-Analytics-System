
# Employee Management & Analytics System

A Python and MySQL Data Engineering project that transforms
employee, salary, and department records into analytics-ready data.

## Tech Stack

- Python
- MySQL 8
- SQLAlchemy
- Pandas
- Streamlit
- Pytest
- GitHub Actions
- Git and GitHub

## Architecture

MySQL Source Tables
        |
        v
Python Extract
        |
        v
Data Transformation
        |
        v
MySQL Analytics Table
        |
        v
Streamlit Dashboard

Incremental ETL uses timestamp-based change detection,
checkpoint tracking, and MySQL upsert operations.

## Features

- Employee and salary data management
- SQL-based employee analytics
- Python ETL pipeline
- Salary and bonus calculations
- Incremental data extraction and loading
- ETL checkpoint management
- Duplicate prevention through primary-key upserts
- Automated data-quality testing
- Streamlit analytics dashboard
- GitHub Actions continuous integration

## Project Structure

Employee_Management_System/
├── .github/workflows/
├── dashboard/
│   └── app.py
├── reports/
├── sql/
├── src/
│   ├── db_connection.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── incremental_extract.py
│   └── incremental_load.py
├── tests/
│   ├── test_data_quality.py
│   ├── test_incremental_etl.py
│   └── test_incremental_integration.py
├── .env.example
├── .gitignore
├── main.py
└── README.md

## Getting Started

### 1. Clone the repository

git clone https://github.com/SrikaarSheela/Employee-Management-Analytics-System.git

cd Employee-Management-Analytics-System

### 2. Create a virtual environment

python3 -m venv .venv

source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure MySQL

Create the company_db database and initialize the
tables using the SQL scripts in the sql/ directory.

### 5. Configure environment variables

Copy .env.example to .env and update your local
database connection settings.

Never commit real database credentials.

### 6. Run the full ETL pipeline

python main.py

### 7. Run incremental ETL

python src/incremental_load.py

### 8. Run automated tests

python -m pytest tests/ -v

### 9. Start the analytics dashboard

streamlit run dashboard/app.py

## Incremental ETL

The incremental pipeline:

1. Reads the previous checkpoint.
2. Identifies changed employee and salary records.
3. Retrieves employee and department information.
4. Calculates total compensation.
5. Inserts or updates the analytics table.
6. Advances the checkpoint within the load transaction.

Timestamp-boundary and concurrent-update handling require
further hardening before production deployment.

## Data Quality

Tests cover:

- Compensation calculations
- Null bonus handling
- Employee change detection
- Salary change detection
- Unchanged record filtering
- Initial extraction behavior
- Duplicate prevention logic
- Analytics-to-source reconciliation
- Checkpoint presence

## Future Improvements

- Stronger concurrency-safe incremental processing
- Automated scheduling
- Data lineage and observability
- Containerized deployment
- Cloud data warehouse integration

## Author

Srikaar Reddy Sheela

Data Engineering Portfolio Project
