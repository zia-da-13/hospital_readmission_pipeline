from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "hospital_readmissions_clean.csv"
)

ENV_FILE = BASE_DIR / ".env"


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv(ENV_FILE)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# Load Processed Data
# --------------------------------------------------

def load_processed_data():
    """Load the cleaned hospital readmission dataset."""

    print("Loading processed data...")

    data = pd.read_csv(PROCESSED_DATA_FILE)

    print(f"Rows loaded: {len(data)}")
    print(f"Columns loaded: {len(data.columns)}")

    return data


# --------------------------------------------------
# Rename Columns
# --------------------------------------------------

def rename_columns(data):
    """Rename CSV columns to match PostgreSQL column names."""

    print("\nRenaming columns for PostgreSQL...")

    column_mapping = {
        "A1Cresult": "a1c_result",
        "glyburide-metformin": "glyburide_metformin",
        "glipizide-metformin": "glipizide_metformin",
        "glimepiride-pioglitazone": "glimepiride_pioglitazone",
        "metformin-rosiglitazone": "metformin_rosiglitazone",
        "metformin-pioglitazone": "metformin_pioglitazone",
        "change": "medication_change",
        "diabetesMed": "diabetes_med",
    }

    data = data.rename(columns=column_mapping)

    print("Columns renamed successfully.")

    return data


# --------------------------------------------------
# Prepare Missing Values
# --------------------------------------------------

def prepare_missing_values(data):
    """Convert pandas missing values to Python None for PostgreSQL."""

    print("\nPreparing missing values...")

    data = data.astype(object).where(pd.notna(data), None)

    print("Missing values prepared successfully.")

    return data


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def connect_to_database():
    """Create and return a PostgreSQL database connection."""

    print("\nConnecting to PostgreSQL...")

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
# Load Data into PostgreSQL
# --------------------------------------------------

def insert_data(connection, data):
    """Insert hospital readmission records into PostgreSQL."""

    print("\nLoading data into PostgreSQL...")

    columns = data.columns.tolist()

    column_names = ", ".join(columns)

    placeholders = ", ".join(["%s"] * len(columns))

    insert_query = f"""
        INSERT INTO hospital_readmissions (
            {column_names}
        )
        VALUES (
            {placeholders}
        )
    """

    records = list(data.itertuples(index=False, name=None))

    with connection.cursor() as cursor:
        cursor.executemany(insert_query, records)

    connection.commit()

    print(f"Rows inserted: {len(records)}")


# --------------------------------------------------
# Verify Database Load
# --------------------------------------------------

def verify_load(connection):
    """Verify the number of records stored in PostgreSQL."""

    print("\nVerifying database load...")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM hospital_readmissions;"
        )

        row_count = cursor.fetchone()[0]

    print(f"Rows in PostgreSQL: {row_count}")

    return row_count


# --------------------------------------------------
# Main Load Pipeline
# --------------------------------------------------

def main():
    """Run the complete PostgreSQL loading process."""

    data = load_processed_data()

    data = rename_columns(data)

    data = prepare_missing_values(data)

    connection = None

    try:
        connection = connect_to_database()

        insert_data(connection, data)

        verify_load(connection)

        print("\nData loading completed successfully.")

    except Exception as error:
        print("\nData loading failed.")
        print(f"Error: {error}")

        if connection is not None:
            connection.rollback()

    finally:
        if connection is not None:
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()