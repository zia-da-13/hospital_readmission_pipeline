from pathlib import Path
import os

import pandas as pd
import plotly.express as px
import psycopg
import streamlit as st
from dotenv import load_dotenv


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Hospital Readmission Analytics",
    page_icon="🏥",
    layout="wide",
)


# --------------------------------------------------
# Project Paths and Environment Variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# Age Group Order
# --------------------------------------------------

AGE_ORDER = [
    "[0-10)",
    "[10-20)",
    "[20-30)",
    "[30-40)",
    "[40-50)",
    "[50-60)",
    "[60-70)",
    "[70-80)",
    "[80-90)",
    "[90-100)",
]


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def get_connection():
    """Create a PostgreSQL database connection."""

    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# --------------------------------------------------
# Load Dashboard Data
# --------------------------------------------------

@st.cache_data
def load_dashboard_data():
    """Load dashboard data from the PostgreSQL star schema."""

    query = """
        SELECT
            f.encounter_id,
            p.patient_nbr,
            p.race,
            p.gender,
            p.age,

            a.admission_type_id,
            a.admission_source_id,
            a.discharge_disposition_id,

            d.diag_1,
            d.diag_2,
            d.diag_3,

            r.readmitted,
            r.readmission_status,

            f.time_in_hospital,
            f.num_lab_procedures,
            f.num_procedures,
            f.num_medications,
            f.number_outpatient,
            f.number_emergency,
            f.number_inpatient,
            f.number_diagnoses,

            f.max_glu_serum,
            f.a1c_result,
            f.insulin,
            f.medication_change,
            f.diabetes_med

        FROM fact_encounter f

        JOIN dim_patient p
            ON f.patient_key = p.patient_key

        JOIN dim_admission a
            ON f.admission_key = a.admission_key

        JOIN dim_diagnosis d
            ON f.diagnosis_key = d.diagnosis_key

        JOIN dim_readmission r
            ON f.readmission_key = r.readmission_key;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                description.name
                for description in cursor.description
            ]

        return pd.DataFrame(
            rows,
            columns=columns,
        )

    finally:
        connection.close()


# --------------------------------------------------
# Load Data
# --------------------------------------------------

try:
    data = load_dashboard_data()

except Exception as error:
    st.error(
        "Unable to load data from the PostgreSQL database."
    )
    st.exception(error)
    st.stop()


# --------------------------------------------------
# Prepare Display Columns
# --------------------------------------------------

data["race_display"] = (
    data["race"]
    .fillna("Unknown")
)

data["a1c_display"] = (
    data["a1c_result"]
    .fillna("Not Tested")
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🏥 Hospital Readmission Analytics")

st.caption(
    "Hospital Readmission & Patient Flow Analytics Platform"
)

st.write(
    "Explore hospital encounters, patient demographics, "
    "clinical utilization, and 30-day readmission patterns."
)

st.divider()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")

st.sidebar.caption(
    "Leave a filter on All to include every category."
)


# Age Filter

selected_age = st.sidebar.selectbox(
    "Age Group",
    options=["All"] + AGE_ORDER,
)


# Gender Filter

gender_options = sorted(
    data["gender"]
    .dropna()
    .unique()
    .tolist()
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    options=["All"] + gender_options,
)


# Race Filter

race_options = sorted(
    data["race_display"]
    .unique()
    .tolist()
)

selected_race = st.sidebar.selectbox(
    "Race",
    options=["All"] + race_options,
)


# Readmission Filter

readmission_options = sorted(
    data["readmission_status"]
    .dropna()
    .unique()
    .tolist()
)

selected_readmission = st.sidebar.selectbox(
    "Readmission Status",
    options=["All"] + readmission_options,
)


# --------------------------------------------------
# Apply Filters
# --------------------------------------------------

filtered_data = data.copy()


if selected_age != "All":
    filtered_data = filtered_data[
        filtered_data["age"] == selected_age
    ]


if selected_gender != "All":
    filtered_data = filtered_data[
        filtered_data["gender"] == selected_gender
    ]


if selected_race != "All":
    filtered_data = filtered_data[
        filtered_data["race_display"] == selected_race
    ]


if selected_readmission != "All":
    filtered_data = filtered_data[
        filtered_data["readmission_status"]
        == selected_readmission
    ]


# --------------------------------------------------
# Empty Filter Check
# --------------------------------------------------

if filtered_data.empty:
    st.warning(
        "No encounters match the selected filters."
    )
    st.stop()


# --------------------------------------------------
# KPI Calculations
# --------------------------------------------------

total_encounters = len(filtered_data)

unique_patients = (
    filtered_data["patient_nbr"]
    .nunique()
)

readmitted_30_days = (
    filtered_data["readmission_status"]
    == "Readmitted Within 30 Days"
).sum()

readmission_rate = (
    readmitted_30_days
    / total_encounters
    * 100
)

average_stay = (
    filtered_data["time_in_hospital"]
    .mean()
)


# --------------------------------------------------
# KPI Cards
# --------------------------------------------------

st.subheader("Executive Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


kpi1.metric(
    label="Total Encounters",
    value=f"{total_encounters:,}",
)


kpi2.metric(
    label="Unique Patients",
    value=f"{unique_patients:,}",
)


kpi3.metric(
    label="30-Day Readmissions",
    value=f"{readmitted_30_days:,}",
)


kpi4.metric(
    label="30-Day Readmission Rate",
    value=f"{readmission_rate:.2f}%",
)


st.metric(
    label="Average Hospital Stay",
    value=f"{average_stay:.2f} days",
)

st.divider()


# --------------------------------------------------
# Readmission Overview
# --------------------------------------------------

st.subheader("Readmission Overview")


readmission_summary = (
    filtered_data
    .groupby(
        "readmission_status",
        as_index=False,
    )
    .size()
    .rename(
        columns={
            "size": "encounters"
        }
    )
)


readmission_chart = px.bar(
    readmission_summary,
    x="readmission_status",
    y="encounters",
    text="encounters",
    title="Encounters by Readmission Status",
    labels={
        "readmission_status": "Readmission Status",
        "encounters": "Encounters",
    },
)


readmission_chart.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
)


st.plotly_chart(
    readmission_chart,
    width="stretch",
)


# --------------------------------------------------
# Age Analysis
# --------------------------------------------------

st.subheader("30-Day Readmission by Age Group")


age_summary = (
    filtered_data
    .groupby(
        "age",
        as_index=False,
        observed=True,
    )
    .agg(
        total_encounters=(
            "encounter_id",
            "count",
        ),
        readmitted_within_30_days=(
            "readmission_status",
            lambda values: (
                values
                == "Readmitted Within 30 Days"
            ).sum(),
        ),
    )
)


age_summary["readmission_rate"] = (
    age_summary["readmitted_within_30_days"]
    / age_summary["total_encounters"]
    * 100
)


age_summary["age"] = pd.Categorical(
    age_summary["age"],
    categories=AGE_ORDER,
    ordered=True,
)


age_summary = age_summary.sort_values("age")


age_chart = px.bar(
    age_summary,
    x="age",
    y="readmission_rate",
    text="readmission_rate",
    title="30-Day Readmission Rate by Age Group",
    labels={
        "age": "Age Group",
        "readmission_rate": "Readmission Rate (%)",
    },
)


age_chart.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)


age_chart.update_yaxes(
    ticksuffix="%"
)


st.plotly_chart(
    age_chart,
    width="stretch",
)


# --------------------------------------------------
# Demographics
# --------------------------------------------------

st.subheader("Patient Demographics")

gender_column, race_column = st.columns(2)


# Gender Chart

with gender_column:

    gender_summary = (
        filtered_data
        .groupby(
            "gender",
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "encounters"
            }
        )
    )

    gender_chart = px.bar(
        gender_summary,
        x="gender",
        y="encounters",
        text="encounters",
        title="Encounters by Gender",
        labels={
            "gender": "Gender",
            "encounters": "Encounters",
        },
    )

    gender_chart.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
    )

    st.plotly_chart(
        gender_chart,
        width="stretch",
    )


# Race Chart

with race_column:

    race_summary = (
        filtered_data
        .groupby(
            "race_display",
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "encounters"
            }
        )
        .sort_values(
            "encounters",
            ascending=True,
        )
    )

    race_chart = px.bar(
        race_summary,
        x="encounters",
        y="race_display",
        orientation="h",
        text="encounters",
        title="Encounters by Race",
        labels={
            "race_display": "Race",
            "encounters": "Encounters",
        },
    )

    race_chart.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
    )

    st.plotly_chart(
        race_chart,
        width="stretch",
    )


# --------------------------------------------------
# Hospital Utilization
# --------------------------------------------------

st.divider()

st.subheader("Hospital Utilization")


utilization1, utilization2, utilization3 = st.columns(3)


utilization1.metric(
    "Average Outpatient Visits",
    f"{filtered_data['number_outpatient'].mean():.2f}",
)


utilization2.metric(
    "Average Emergency Visits",
    f"{filtered_data['number_emergency'].mean():.2f}",
)


utilization3.metric(
    "Average Previous Inpatient Visits",
    f"{filtered_data['number_inpatient'].mean():.2f}",
)


# --------------------------------------------------
# Previous Inpatient Visits
# --------------------------------------------------

st.subheader(
    "Previous Inpatient Visits and Readmission Risk"
)


inpatient_summary = (
    filtered_data
    .groupby(
        "number_inpatient",
        as_index=False,
    )
    .agg(
        total_encounters=(
            "encounter_id",
            "count",
        ),
        readmitted_within_30_days=(
            "readmission_status",
            lambda values: (
                values
                == "Readmitted Within 30 Days"
            ).sum(),
        ),
    )
)


inpatient_summary["readmission_rate"] = (
    inpatient_summary["readmitted_within_30_days"]
    / inpatient_summary["total_encounters"]
    * 100
)


# Keep categories with enough encounters for a
# meaningful main visualization.
inpatient_chart_data = inpatient_summary[
    inpatient_summary["total_encounters"] >= 100
].copy()


inpatient_chart = px.line(
    inpatient_chart_data,
    x="number_inpatient",
    y="readmission_rate",
    markers=True,
    hover_data={
        "total_encounters": True,
        "readmitted_within_30_days": True,
        "readmission_rate": ":.2f",
    },
    title=(
        "30-Day Readmission Rate by "
        "Previous Inpatient Visits"
    ),
    labels={
        "number_inpatient":
            "Previous Inpatient Visits",
        "readmission_rate":
            "Readmission Rate (%)",
        "total_encounters":
            "Total Encounters",
        "readmitted_within_30_days":
            "30-Day Readmissions",
    },
)


inpatient_chart.update_yaxes(
    ticksuffix="%"
)


st.plotly_chart(
    inpatient_chart,
    width="stretch",
)


st.caption(
    "The main utilization chart includes groups with at "
    "least 100 encounters to reduce distortion from very "
    "small sample sizes."
)


# --------------------------------------------------
# Clinical Utilization
# --------------------------------------------------

st.divider()

st.subheader("Clinical Utilization by Readmission Status")


clinical_summary = (
    filtered_data
    .groupby(
        "readmission_status",
        as_index=False,
    )
    .agg(
        average_hospital_days=(
            "time_in_hospital",
            "mean",
        ),
        average_lab_procedures=(
            "num_lab_procedures",
            "mean",
        ),
        average_procedures=(
            "num_procedures",
            "mean",
        ),
        average_medications=(
            "num_medications",
            "mean",
        ),
        average_diagnoses=(
            "number_diagnoses",
            "mean",
        ),
    )
)


st.dataframe(
    clinical_summary.round(2),
    width="stretch",
    hide_index=True,
)


# --------------------------------------------------
# A1C Analysis
# --------------------------------------------------

st.subheader("A1C Testing and Readmission")


a1c_summary = (
    filtered_data
    .groupby(
        "a1c_display",
        as_index=False,
    )
    .agg(
        total_encounters=(
            "encounter_id",
            "count",
        ),
        readmitted_within_30_days=(
            "readmission_status",
            lambda values: (
                values
                == "Readmitted Within 30 Days"
            ).sum(),
        ),
    )
)


a1c_summary["readmission_rate"] = (
    a1c_summary["readmitted_within_30_days"]
    / a1c_summary["total_encounters"]
    * 100
)


a1c_chart = px.bar(
    a1c_summary,
    x="a1c_display",
    y="readmission_rate",
    text="readmission_rate",
    hover_data={
        "total_encounters": True,
        "readmitted_within_30_days": True,
    },
    title="30-Day Readmission Rate by A1C Result",
    labels={
        "a1c_display": "A1C Result",
        "readmission_rate": "Readmission Rate (%)",
        "total_encounters": "Total Encounters",
        "readmitted_within_30_days":
            "30-Day Readmissions",
    },
)


a1c_chart.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)


a1c_chart.update_yaxes(
    ticksuffix="%"
)


st.plotly_chart(
    a1c_chart,
    width="stretch",
)


# --------------------------------------------------
# Encounter Data
# --------------------------------------------------

st.divider()


with st.expander("Explore Encounter Data"):

    st.write(
        f"Showing {len(filtered_data):,} encounters."
    )

    st.dataframe(
        filtered_data,
        width="stretch",
        hide_index=True,
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Hospital Readmission & Patient Flow Analytics Platform "
    "| Python • PostgreSQL • Streamlit • Plotly"
)