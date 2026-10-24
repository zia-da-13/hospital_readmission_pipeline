from pathlib import Path
from datetime import datetime
import os

import psycopg
from dotenv import load_dotenv


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
LOG_DIR = BASE_DIR / "logs"

load_dotenv(ENV_FILE)


# --------------------------------------------------
# Database Configuration
# --------------------------------------------------

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def connect_to_database():
    """Connect to PostgreSQL."""

    print("Connecting to PostgreSQL...")

    connection = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    print("Database connection successful.")

    return connection


# --------------------------------------------------
# Run Single Quality Check
# --------------------------------------------------

def run_check(cursor, check_name, query, expected_value):
    """Run a data-quality query and compare it with the expected value."""

    cursor.execute(query)

    actual_value = cursor.fetchone()[0]

    status = "PASS" if actual_value == expected_value else "FAIL"

    result = {
        "check": check_name,
        "expected": expected_value,
        "actual": actual_value,
        "status": status,
    }

    return result


# --------------------------------------------------
# Data Quality Checks
# --------------------------------------------------

def run_data_quality_checks(connection):
    """Run all database data-quality checks."""

    results = []

    with connection.cursor() as cursor:

        results.append(
            run_check(
                cursor,
                "Hospital readmission row count",
                """
                SELECT COUNT(*)
                FROM hospital_readmissions;
                """,
                101766,
            )
        )

        results.append(
            run_check(
                cursor,
                "Fact encounter row count",
                """
                SELECT COUNT(*)
                FROM fact_encounter;
                """,
                101766,
            )
        )

        results.append(
            run_check(
                cursor,
                "Duplicate encounter IDs",
                """
                SELECT COUNT(*)
                FROM (
                    SELECT encounter_id
                    FROM hospital_readmissions
                    GROUP BY encounter_id
                    HAVING COUNT(*) > 1
                ) duplicates;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing encounter IDs",
                """
                SELECT COUNT(*)
                FROM hospital_readmissions
                WHERE encounter_id IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing patient numbers",
                """
                SELECT COUNT(*)
                FROM hospital_readmissions
                WHERE patient_nbr IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Invalid hospital stay values",
                """
                SELECT COUNT(*)
                FROM hospital_readmissions
                WHERE time_in_hospital < 1
                   OR time_in_hospital > 14;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Invalid readmission categories",
                """
                SELECT COUNT(*)
                FROM hospital_readmissions
                WHERE readmitted NOT IN ('NO', '<30', '>30')
                   OR readmitted IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing fact patient keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter
                WHERE patient_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing fact admission keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter
                WHERE admission_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing fact diagnosis keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter
                WHERE diagnosis_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Missing fact readmission keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter
                WHERE readmission_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Orphaned patient foreign keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter f
                LEFT JOIN dim_patient p
                    ON f.patient_key = p.patient_key
                WHERE p.patient_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Orphaned admission foreign keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter f
                LEFT JOIN dim_admission a
                    ON f.admission_key = a.admission_key
                WHERE a.admission_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Orphaned diagnosis foreign keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter f
                LEFT JOIN dim_diagnosis d
                    ON f.diagnosis_key = d.diagnosis_key
                WHERE d.diagnosis_key IS NULL;
                """,
                0,
            )
        )

        results.append(
            run_check(
                cursor,
                "Orphaned readmission foreign keys",
                """
                SELECT COUNT(*)
                FROM fact_encounter f
                LEFT JOIN dim_readmission r
                    ON f.readmission_key = r.readmission_key
                WHERE r.readmission_key IS NULL;
                """,
                0,
            )
        )

    return results


# --------------------------------------------------
# Display Results
# --------------------------------------------------

def display_results(results):
    """Display data-quality results in the terminal."""

    print("\nData Quality Results")
    print("=" * 70)

    for result in results:
        print(
            f"{result['status']:<6} | "
            f"{result['check']:<35} | "
            f"Expected: {result['expected']:<8} | "
            f"Actual: {result['actual']}"
        )

    print("=" * 70)

    passed = sum(
        1 for result in results
        if result["status"] == "PASS"
    )

    failed = len(results) - passed

    print(f"Checks passed: {passed}")
    print(f"Checks failed: {failed}")


# --------------------------------------------------
# Write Log File
# --------------------------------------------------

def write_log(results):
    """Write data-quality results to a log file."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    log_file = LOG_DIR / f"data_quality_{timestamp}.log"

    with open(log_file, "w", encoding="utf-8") as file:

        file.write("Hospital Readmission Data Quality Report\n")
        file.write("=" * 60 + "\n")
        file.write(f"Run time: {datetime.now()}\n\n")

        for result in results:
            file.write(
                f"{result['status']} | "
                f"{result['check']} | "
                f"Expected: {result['expected']} | "
                f"Actual: {result['actual']}\n"
            )

        passed = sum(
            1 for result in results
            if result["status"] == "PASS"
        )

        failed = len(results) - passed

        file.write("\n")
        file.write(f"Checks passed: {passed}\n")
        file.write(f"Checks failed: {failed}\n")

    print(f"\nLog file created: {log_file}")


# --------------------------------------------------
# Main Program
# --------------------------------------------------

def main():
    """Run the complete data-quality process."""

    connection = None

    try:
        connection = connect_to_database()

        results = run_data_quality_checks(connection)

        display_results(results)

        write_log(results)

        failed_checks = [
            result
            for result in results
            if result["status"] == "FAIL"
        ]

        if failed_checks:
            print("\nData quality checks completed with failures.")
        else:
            print("\nAll data quality checks passed successfully.")

    except Exception as error:
        print("\nData quality process failed.")
        print(f"Error: {error}")

    finally:
        if connection is not None:
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()