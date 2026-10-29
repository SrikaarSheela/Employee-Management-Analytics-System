
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

# Import our existing database connection
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from db_connection import engine

st.set_page_config(
    page_title="Employee Management Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Employee Management & Analytics System")
st.caption("MySQL | Python | Pandas | Streamlit")

# Read data directly from MySQL
def load_dashboard_data():
    query = text("""
        SELECT
            employee_id,
            employee_name,
            job_title,
            department_name,
            location,
            salary_amount,
            bonus,
            total_compensation
        FROM employee_salary_analytics
        ORDER BY employee_id
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


try:
    df = load_dashboard_data()
except Exception as error:
    st.error("Unable to connect to the analytics database.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning("No employee data found. Run python main.py first.")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

departments = sorted(df["department_name"].unique())

selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=departments,
    default=departments
)

filtered_df = df[
    df["department_name"].isin(selected_departments)
].copy()

if filtered_df.empty:
    st.warning("No employees match the selected filters.")
    st.stop()

# KPI calculations
total_employees = len(filtered_df)
total_departments = filtered_df["department_name"].nunique()
total_salary = filtered_df["salary_amount"].sum()
total_compensation = filtered_df["total_compensation"].sum()

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Employees", total_employees)
col2.metric("Departments", total_departments)
col3.metric("Annual Salary", f"${total_salary:,.2f}")
col4.metric(
    "Total Compensation",
    f"${total_compensation:,.2f}"
)

st.divider()

# Department analytics
department_summary = (
    filtered_df.groupby("department_name", as_index=False)
    .agg(
        employee_count=("employee_id", "count"),
        total_salary=("salary_amount", "sum"),
        avg_salary=("salary_amount", "mean")
    )
)

left, right = st.columns(2)

with left:
    st.subheader("Annual Salary by Department")

    fig_salary = px.bar(
        department_summary,
        x="department_name",
        y="total_salary",
        color="department_name",
        labels={
            "department_name": "Department",
            "total_salary": "Annual Salary"
        }
    )

    fig_salary.update_layout(showlegend=False)
    st.plotly_chart(fig_salary, use_container_width=True)

with right:
    st.subheader("Employees by Department")

    fig_employees = px.pie(
        department_summary,
        names="department_name",
        values="employee_count",
        hole=0.4
    )

    st.plotly_chart(fig_employees, use_container_width=True)

# Employee records
st.subheader("Employee Salary Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Download report
csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Employee Report",
    data=csv_data,
    file_name="employee_analytics_report.csv",
    mime="text/csv"
)

st.caption("Source: company_db.employee_salary_analytics")


# PROJECT ANALYTICS
st.divider()
st.header("Project Analytics")

project_query = text("""
    SELECT
        project_id,
        project_name,
        department_name,
        start_date,
        end_date,
        project_status,
        assigned_employees
    FROM vw_project_analytics
    ORDER BY project_id
""")

with engine.connect() as connection:
    projects_df = pd.read_sql(project_query, connection)

if not projects_df.empty:
    p1, p2, p3 = st.columns(3)

    p1.metric("Total Projects", len(projects_df))
    p2.metric(
        "In Progress",
        int((projects_df["project_status"] == "In Progress").sum())
    )
    p3.metric(
        "Completed",
        int((projects_df["project_status"] == "Completed").sum())
    )

    fig_projects = px.bar(
        projects_df,
        x="project_name",
        y="assigned_employees",
        color="project_status",
        title="Employees Assigned by Project"
    )

    st.plotly_chart(fig_projects, use_container_width=True)

    st.dataframe(
        projects_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No project records found.")



# ATTENDANCE ANALYTICS
st.divider()
st.header("Employee Attendance Analytics")

attendance_query = text("""
    SELECT
        employee_id,
        employee_name,
        department_name,
        recorded_days,
        present_days,
        absent_days,
        leave_days
    FROM vw_attendance_analytics
    ORDER BY employee_id
""")

with engine.connect() as connection:
    attendance_df = pd.read_sql(
        attendance_query, connection
    )

if not attendance_df.empty:

    total_present = int(attendance_df["present_days"].sum())
    total_absent = int(attendance_df["absent_days"].sum())
    total_leave = int(attendance_df["leave_days"].sum())

    total_recorded = int(attendance_df["recorded_days"].sum())

    attendance_rate = (
        total_present / total_recorded * 100
        if total_recorded > 0 else 0
    )

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Present Days", total_present)
    a2.metric("Absent Days", total_absent)
    a3.metric("Leave Days", total_leave)
    a4.metric("Attendance Rate", f"{attendance_rate:.1f}%")

    # Employee attendance percentage
    attendance_df["attendance_percentage"] = (
        attendance_df["present_days"]
        .div(attendance_df["recorded_days"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
        .round(2)
    )

    fig_attendance = px.bar(
        attendance_df,
        x="employee_name",
        y="attendance_percentage",
        color="department_name",
        title="Employee Attendance Percentage",
        labels={
            "employee_name": "Employee",
            "attendance_percentage": "Attendance %"
        }
    )

    st.plotly_chart(
        fig_attendance,
        use_container_width=True
    )

    st.subheader("Attendance Details")

    st.dataframe(
        attendance_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Attendance rate is based on recorded attendance "
        "days only. Employees without records are not "
        "included in the overall rate denominator."
    )

else:
    st.info("No attendance records available.")


# DATA QUALITY MONITORING
st.divider()
st.header("Data Quality Monitoring")

# Retrieve the latest result for each validation check
quality_query = text("""
    SELECT
        d.check_name,
        d.check_status,
        d.issue_count,
        d.checked_at
    FROM data_quality_results d
    INNER JOIN (
        SELECT
            check_name,
            MAX(check_id) AS latest_check_id
        FROM data_quality_results
        GROUP BY check_name
    ) latest
        ON d.check_id = latest.latest_check_id
    ORDER BY d.check_name
""")

with engine.connect() as connection:
    quality_df = pd.read_sql(quality_query, connection)

if not quality_df.empty:

    # Calculate validation KPIs
    total_checks = len(quality_df)

    passed_checks = int(
        (quality_df["check_status"] == "PASS").sum()
    )

    failed_checks = int(
        (quality_df["check_status"] == "FAIL").sum()
    )

    total_issues = int(quality_df["issue_count"].sum())

    pass_rate = (
        passed_checks / total_checks * 100
        if total_checks > 0 else 0
    )

    # KPI cards
    q1, q2, q3, q4 = st.columns(4)

    q1.metric("Total Checks", total_checks)
    q2.metric("Passed Checks", passed_checks)
    q3.metric("Failed Checks", failed_checks)
    q4.metric("Data Quality Pass Rate", f"{pass_rate:.1f}%")

    st.divider()

    # Validation status chart
    status_summary = pd.DataFrame({
        "Status": ["PASS", "FAIL"],
        "Count": [passed_checks, failed_checks]
    })

    fig_quality = px.bar(
        status_summary,
        x="Status",
        y="Count",
        color="Status",
        color_discrete_map={
            "PASS": "#16A34A",
            "FAIL": "#DC2626"
        },
        title="Data Quality Validation Results"
    )

    st.plotly_chart(
        fig_quality,
        use_container_width=True
    )

    # Display individual checks
    st.subheader("Validation Check Details")

    st.dataframe(
        quality_df,
        use_container_width=True,
        hide_index=True
    )

    # Overall validation result
    if failed_checks == 0 and total_issues == 0:
        st.success(
            "All data quality checks passed successfully!"
        )
    else:
        st.error(
            f"Data quality validation found "
            f"{total_issues} issue(s)."
        )

    # Show latest execution timestamp
    latest_check = quality_df["checked_at"].max()

    st.caption(
        f"Latest validation recorded: {latest_check}"
    )

else:
    st.warning(
        "No data quality results available. "
        "Run sp_validate_employee_data() in MySQL."
    )


# ETL PIPELINE MONITORING
st.divider()
st.header("ETL Pipeline Execution Monitoring")

pipeline_query = text("""
    SELECT
        run_id,
        pipeline_name,
        start_time,
        end_time,
        status,
        extracted_records,
        loaded_records,
        execution_seconds,
        error_message
    FROM etl_pipeline_runs
    ORDER BY run_id DESC
""")

with engine.connect() as connection:
    pipeline_df = pd.read_sql(
        pipeline_query, connection
    )

if not pipeline_df.empty:

    total_runs = len(pipeline_df)
    successful_runs = int(
        (pipeline_df["status"] == "SUCCESS").sum()
    )
    failed_runs = int(
        (pipeline_df["status"] == "FAILED").sum()
    )

    completed_df = pipeline_df[
        pipeline_df["status"].isin(["SUCCESS", "FAILED"])
    ]

    avg_duration = (
        completed_df["execution_seconds"].mean()
        if not completed_df.empty else 0
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Total Pipeline Runs", total_runs)
    m2.metric("Successful Runs", successful_runs)
    m3.metric("Failed Runs", failed_runs)
    m4.metric(
        "Average Duration",
        f"{avg_duration:.3f} sec"
    )

    st.subheader("Pipeline Execution History")

    st.dataframe(
        pipeline_df,
        use_container_width=True,
        hide_index=True
    )

    # Execution duration trend
    trend_df = completed_df.sort_values("run_id")

    if not trend_df.empty:
        fig_runs = px.line(
            trend_df,
            x="run_id",
            y="execution_seconds",
            markers=True,
            title="ETL Pipeline Execution Duration",
            labels={
                "run_id": "Run ID",
                "execution_seconds": "Duration (seconds)"
            }
        )

        st.plotly_chart(
            fig_runs,
            use_container_width=True
        )

    latest_run = pipeline_df.iloc[0]

    if latest_run["status"] == "SUCCESS":
        st.success("Latest ETL pipeline run succeeded.")
    elif latest_run["status"] == "FAILED":
        st.error("Latest ETL pipeline run failed.")
        st.write(latest_run["error_message"])
    else:
        st.info("Latest ETL pipeline run is still running.")

else:
    st.info("No ETL pipeline execution history available.")

