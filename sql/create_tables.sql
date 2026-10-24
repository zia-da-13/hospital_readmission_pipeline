-- ============================================================
-- Hospital Readmission Analytics Platform
-- PostgreSQL Table Creation Script
-- ============================================================


-- ------------------------------------------------------------
-- Drop Existing Table
-- ------------------------------------------------------------

DROP TABLE IF EXISTS hospital_readmissions;


-- ------------------------------------------------------------
-- Create Hospital Readmissions Table
-- ------------------------------------------------------------

CREATE TABLE hospital_readmissions (

    encounter_id BIGINT PRIMARY KEY,

    patient_nbr BIGINT,

    race TEXT,

    gender TEXT,

    age TEXT,

    admission_type_id INTEGER,

    discharge_disposition_id INTEGER,

    admission_source_id INTEGER,

    time_in_hospital INTEGER,

    num_lab_procedures INTEGER,

    num_procedures INTEGER,

    num_medications INTEGER,

    number_outpatient INTEGER,

    number_emergency INTEGER,

    number_inpatient INTEGER,

    diag_1 TEXT,

    diag_2 TEXT,

    diag_3 TEXT,

    number_diagnoses INTEGER,

    max_glu_serum TEXT,

    a1c_result TEXT,

    metformin TEXT,

    repaglinide TEXT,

    nateglinide TEXT,

    chlorpropamide TEXT,

    glimepiride TEXT,

    acetohexamide TEXT,

    glipizide TEXT,

    glyburide TEXT,

    tolbutamide TEXT,

    pioglitazone TEXT,

    rosiglitazone TEXT,

    acarbose TEXT,

    miglitol TEXT,

    troglitazone TEXT,

    tolazamide TEXT,

    examide TEXT,

    citoglipton TEXT,

    insulin TEXT,

    glyburide_metformin TEXT,

    glipizide_metformin TEXT,

    glimepiride_pioglitazone TEXT,

    metformin_rosiglitazone TEXT,

    metformin_pioglitazone TEXT,

    medication_change TEXT,

    diabetes_med TEXT,

    readmitted TEXT,

    readmission_status TEXT

);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------

CREATE INDEX idx_hospital_readmissions_patient
ON hospital_readmissions(patient_nbr);


CREATE INDEX idx_hospital_readmissions_readmitted
ON hospital_readmissions(readmitted);


CREATE INDEX idx_hospital_readmissions_status
ON hospital_readmissions(readmission_status);


CREATE INDEX idx_hospital_readmissions_admission_type
ON hospital_readmissions(admission_type_id);


-- ------------------------------------------------------------
-- Confirm Table Creation
-- ------------------------------------------------------------

SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;