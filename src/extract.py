from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

DIABETIC_DATA_FILE = RAW_DATA_DIR / "diabetic_data.csv"


# --------------------------------------------------
# Load Data
# --------------------------------------------------

def load_data():
    """Load the raw hospital readmission dataset."""

    print("Loading hospital readmission data...")

    data = pd.read_csv(DIABETIC_DATA_FILE)

    print("Data loaded successfully.")

    return data


# --------------------------------------------------
# Inspect Dataset
# --------------------------------------------------

def inspect_data(data):
    """Display basic information about the dataset."""

    print("\nDataset shape:")
    print(data.shape)

    print("\nColumn names:")
    print(data.columns.tolist())

    print("\nFirst 5 rows:")
    print(data.head())


# --------------------------------------------------
# Inspect Data Quality
# --------------------------------------------------

def inspect_data_quality(data):
    """Display data types and missing-value information."""

    print("\nData types:")
    print(data.dtypes)

    print("\nMissing values:")
    print(data.isnull().sum())

    print("\nQuestion mark values:")
    print((data == "?").sum())


# --------------------------------------------------
# Main Program
# --------------------------------------------------

if __name__ == "__main__":
    hospital_data = load_data()

    inspect_data(hospital_data)

    inspect_data_quality(hospital_data)