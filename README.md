# Employee Management & Analytics System

## Project Overview

An end-to-end Data Engineering project that extracts employee information from MySQL, transforms data using Python and Pandas, loads analytical results into MySQL, and presents business insights through an interactive Streamlit dashboard.

## Technology Stack

- **Database:** MySQL
- **Programming:** Python 3
- **Data Processing:** Pandas
- **Database Connectivity:** SQLAlchemy and PyMySQL
- **Dashboard:** Streamlit and Plotly
- **Testing:** Pytest
- **Version Control:** Git and GitHub

## Key Features

- Employee, department, salary, project, and attendance data management
- Automated Extract, Transform, Load (ETL) pipeline
- Salary and total compensation analytics
- Interactive department and project dashboards
- Attendance reporting
- Automated SQL data quality checks
- Pipeline execution history and error logging
- Automated Python data validation tests

## ETL Architecture

MySQL Source Tables → Python Extraction → CSV Files → Pandas Transformation → MySQL Analytics Table → Streamlit Dashboard

## Sample Data

The project uses synthetic employee data for development and demonstration.

- 10 employees
- 5 departments
- 5 projects
- 50 records across six source tables
- $1,035,000 annual salary total
- $1,109,000 total compensation

## Local Setup

1. Install Python and MySQL.
2. Clone the repository.
3. Create and activate a Python virtual environment.
4. Install dependencies using `pip install -r requirements.txt`.
5. Configure `.env` using `.env.example`.
6. Initialize and populate the MySQL database using the project's SQL setup scripts.
7. Run the ETL pipeline with `python main.py`.
8. Run the dashboard with `python -m streamlit run dashboard/app.py`.

## Automated Testing

Run:

`python -m pytest tests/ -v`

The current project includes 10 automated data quality tests.

## Future Improvements

- Incremental ETL processing
- CI/CD with GitHub Actions
- Historical salary tracking
- Advanced attendance reporting
- Scheduled pipeline execution
- Containerized deployment

## Purpose

Built as a hands-on Data Engineering portfolio project demonstrating SQL, Python, ETL development, data quality validation, analytics, testing, and pipeline monitoring.