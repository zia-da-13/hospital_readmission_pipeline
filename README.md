# Hospital Readmission & Patient Flow Analytics Platform

## Project Overview

The Hospital Readmission & Patient Flow Analytics Platform is an end-to-end data engineering and analytics project designed to analyze hospital encounters, patient utilization, and readmission patterns.

The project demonstrates a complete analytics workflow using Python, PostgreSQL, SQL, Streamlit, Power BI, and GitHub.

The pipeline extracts and cleans hospital encounter data, loads it into PostgreSQL, transforms it into an analytics-ready star schema, validates data quality, performs SQL analysis, and presents insights through interactive Streamlit and Power BI dashboards.

---

## Project Objectives

The main objectives of this project are to:

- Build a reproducible healthcare data pipeline.
- Clean and transform raw hospital encounter data.
- Store processed data in PostgreSQL.
- Design an analytics-ready star schema.
- Implement automated data-quality checks.
- Analyze hospital readmission patterns using SQL.
- Identify factors associated with 30-day readmissions.
- Build interactive dashboards using Streamlit and Power BI.
- Demonstrate an end-to-end data engineering and analytics workflow.

---

## Dataset

This project uses the **Diabetes 130-US Hospitals for Years 1999–2008** dataset from the UCI Machine Learning Repository.

The dataset contains:

- **101,766 hospital encounters**
- **71,518 unique patients**
- Demographic information
- Admission and discharge information
- Diagnoses
- Laboratory procedures
- Medication information
- Previous inpatient, outpatient, and emergency visits
- Hospital readmission outcomes

The original dataset contains 50 columns.

Raw data files are not stored in the GitHub repository.

---

## Technology Stack

- **Python**
- **Pandas**
- **PostgreSQL**
- **psycopg**
- **SQL**
- **Streamlit**
- **Plotly**
- **Power BI**
- **Git**
- **GitHub**
- **VS Code**

---

## Project Architecture

```text
Raw Hospital Data
        |
        v
Python Extraction
        |
        v
Data Cleaning & Transformation
        |
        v
Processed CSV
        |
        v
PostgreSQL
        |
        v
Analytics Star Schema
        |
        +-------------------+
        |                   |
        v                   v
   SQL Analytics       Data Quality
        |                   |
        +---------+---------+
                  |
                  v
        Analytics & Reporting
             /         \
            v           v
       Streamlit     Power BI