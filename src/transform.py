from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

RAW_DATA_FILE = RAW_DATA_DIR / "diabetic_data.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "hospital_readmissions_clean.csv"


# --------------------------------------------------
# Load Raw Data
# --------------------------------------------------

def load_raw_data():
    """Load the raw hospital readmission dataset."""

    print("Loading raw data...")

    data = pd.read_csv(RAW_DATA_FILE)

    print(f"Raw rows: {len(data)}")
    print(f"Raw columns: {len(data.columns)}")

    return data


# --------------------------------------------------
# Replace Missing Value Symbols
# --------------------------------------------------

def replace_missing_values(data):
    """Replace question marks with proper missing values."""

    print("\nReplacing '?' values with missing values...")

    data = data.replace("?", pd.NA)

    return data


# --------------------------------------------------
# Remove Duplicate Rows
# --------------------------------------------------

def remove_duplicates(data):
    """Remove duplicate rows from the dataset."""

    duplicate_count = data.duplicated().sum()

    print(f"\nDuplicate rows found: {duplicate_count}")

    data = data.drop_duplicates()

    print(f"Rows after duplicate removal: {len(data)}")

    return data


# --------------------------------------------------
# Remove High-Missing Columns
# --------------------------------------------------

def remove_columns(data):
    """Remove columns with excessive missing values."""

    columns_to_remove = [
        "weight",
        "payer_code",
        "medical_specialty",
    ]

    print("\nRemoving high-missing columns:")

    for column in columns_to_remove:
        if column in data.columns:
            print(f"- {column}")

    data = data.drop(columns=columns_to_remove)

    return data


# --------------------------------------------------
# Create Readmission Status
# --------------------------------------------------

def create_readmission_status(data):
    """Create a clearer readmission status column."""

    print("\nCreating readmission status...")

    readmission_mapping = {
        "NO": "Not Readmitted",
        ">30": "Readmitted After 30 Days",
        "<30": "Readmitted Within 30 Days",
    }

    data["readmission_status"] = data["readmitted"].map(
        readmission_mapping
    )

    return data


# --------------------------------------------------
# Display Transformation Summary
# --------------------------------------------------

def display_summary(data):
    """Display information about the transformed dataset."""

    print("\nTransformation Summary")
    print("----------------------")

    print(f"Final rows: {len(data)}")
    print(f"Final columns: {len(data.columns)}")

    print("\nReadmission distribution:")
    print(data["readmission_status"].value_counts())

    print("\nRemaining missing values:")
    missing_values = data.isnull().sum()

    print(missing_values[missing_values > 0].sort_values(ascending=False))


# --------------------------------------------------
# Save Processed Data
# --------------------------------------------------

def save_processed_data(data):
    """Save the transformed dataset."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    data.to_csv(
        PROCESSED_DATA_FILE,
        index=False,
    )

    print("\nProcessed data saved successfully.")
    print(f"File: {PROCESSED_DATA_FILE}")


# --------------------------------------------------
# Main Transformation Pipeline
# --------------------------------------------------

def main():
    """Run the complete transformation process."""

    data = load_raw_data()

    data = replace_missing_values(data)

    data = remove_duplicates(data)

    data = remove_columns(data)

    data = create_readmission_status(data)

    display_summary(data)

    save_processed_data(data)


if __name__ == "__main__":
    main()