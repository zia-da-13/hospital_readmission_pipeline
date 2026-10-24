-- ============================================================
-- Hospital Readmission Analytics Platform
-- Analytics Star Schema
-- ============================================================


-- ------------------------------------------------------------
-- Drop Existing Analytics Tables
-- ------------------------------------------------------------

DROP TABLE IF EXISTS fact_encounter;
DROP TABLE IF EXISTS dim_readmission;
DROP TABLE IF EXISTS dim_diagnosis;
DROP TABLE IF EXISTS dim_admission;
DROP TABLE IF EXISTS dim_patient;


-- ============================================================
-- 1. Patient Dimension
-- ============================================================

CREATE TABLE dim_patient (
    patient_key BIGSERIAL PRIMARY KEY,
    patient_nbr BIGINT UNIQUE NOT NULL,
    race TEXT,
    gender TEXT,
    age TEXT
);


INSERT INTO dim_patient (
    patient_nbr,
    race,
    gender,
    age
)
SELECT DISTINCT ON (patient_nbr)
    patient_nbr,
    race,
    gender,
    age
FROM hospital_readmissions
ORDER BY patient_nbr, encounter_id;


-- ============================================================
-- 2. Admission Dimension
-- ============================================================

CREATE TABLE dim_admission (
    admission_key BIGSERIAL PRIMARY KEY,
    admission_type_id INTEGER,
    admission_source_id INTEGER,
    discharge_disposition_id INTEGER,

    UNIQUE (
        admission_type_id,
        admission_source_id,
        discharge_disposition_id
    )
);


INSERT INTO dim_admission (
    admission_type_id,
    admission_source_id,
    discharge_disposition_id
)
SELECT DISTINCT
    admission_type_id,
    admission_source_id,
    discharge_disposition_id
FROM hospital_readmissions;


-- ============================================================
-- 3. Diagnosis Dimension
-- ============================================================

CREATE TABLE dim_diagnosis (
    diagnosis_key BIGSERIAL PRIMARY KEY,
    diag_1 TEXT,
    diag_2 TEXT,
    diag_3 TEXT,

    UNIQUE (
        diag_1,
        diag_2,
        diag_3
    )
);


INSERT INTO dim_diagnosis (
    diag_1,
    diag_2,
    diag_3
)
SELECT DISTINCT
    diag_1,
    diag_2,
    diag_3
FROM hospital_readmissions;


-- ============================================================
-- 4. Readmission Dimension
-- ============================================================

CREATE TABLE dim_readmission (
    readmission_key BIGSERIAL PRIMARY KEY,
    readmitted TEXT UNIQUE NOT NULL,
    readmission_status TEXT NOT NULL
);


INSERT INTO dim_readmission (
    readmitted,
    readmission_status
)
SELECT DISTINCT
    readmitted,
    readmission_status
FROM hospital_readmissions;


-- ============================================================
-- 5. Encounter Fact Table
-- ============================================================

CREATE TABLE fact_encounter (
    encounter_id BIGINT PRIMARY KEY,

    patient_key BIGINT NOT NULL,
    admission_key BIGINT NOT NULL,
    diagnosis_key BIGINT NOT NULL,
    readmission_key BIGINT NOT NULL,

    time_in_hospital INTEGER,
    num_lab_procedures INTEGER,
    num_procedures INTEGER,
    num_medications INTEGER,

    number_outpatient INTEGER,
    number_emergency INTEGER,
    number_inpatient INTEGER,

    number_diagnoses INTEGER,

    max_glu_serum TEXT,
    a1c_result TEXT,

    insulin TEXT,
    medication_change TEXT,
    diabetes_med TEXT,

    CONSTRAINT fk_fact_patient
        FOREIGN KEY (patient_key)
        REFERENCES dim_patient(patient_key),

    CONSTRAINT fk_fact_admission
        FOREIGN KEY (admission_key)
        REFERENCES dim_admission(admission_key),

    CONSTRAINT fk_fact_diagnosis
        FOREIGN KEY (diagnosis_key)
        REFERENCES dim_diagnosis(diagnosis_key),

    CONSTRAINT fk_fact_readmission
        FOREIGN KEY (readmission_key)
        REFERENCES dim_readmission(readmission_key)
);


-- ============================================================
-- 6. Load Encounter Fact Table
-- ============================================================

INSERT INTO fact_encounter (
    encounter_id,
    patient_key,
    admission_key,
    diagnosis_key,
    readmission_key,
    time_in_hospital,
    num_lab_procedures,
    num_procedures,
    num_medications,
    number_outpatient,
    number_emergency,
    number_inpatient,
    number_diagnoses,
    max_glu_serum,
    a1c_result,
    insulin,
    medication_change,
    diabetes_med
)
SELECT
    h.encounter_id,
    p.patient_key,
    a.admission_key,
    d.diagnosis_key,
    r.readmission_key,
    h.time_in_hospital,
    h.num_lab_procedures,
    h.num_procedures,
    h.num_medications,
    h.number_outpatient,
    h.number_emergency,
    h.number_inpatient,
    h.number_diagnoses,
    h.max_glu_serum,
    h.a1c_result,
    h.insulin,
    h.medication_change,
    h.diabetes_med

FROM hospital_readmissions h

JOIN dim_patient p
    ON h.patient_nbr = p.patient_nbr

JOIN dim_admission a
    ON h.admission_type_id = a.admission_type_id
    AND h.admission_source_id = a.admission_source_id
    AND h.discharge_disposition_id = a.discharge_disposition_id

JOIN dim_diagnosis d
    ON d.diag_1 IS NOT DISTINCT FROM h.diag_1
    AND d.diag_2 IS NOT DISTINCT FROM h.diag_2
    AND d.diag_3 IS NOT DISTINCT FROM h.diag_3

JOIN dim_readmission r
    ON h.readmitted = r.readmitted;


-- ============================================================
-- 7. Create Fact Table Indexes
-- ============================================================

CREATE INDEX idx_fact_encounter_patient
ON fact_encounter(patient_key);

CREATE INDEX idx_fact_encounter_admission
ON fact_encounter(admission_key);

CREATE INDEX idx_fact_encounter_diagnosis
ON fact_encounter(diagnosis_key);

CREATE INDEX idx_fact_encounter_readmission
ON fact_encounter(readmission_key);


-- ============================================================
-- 8. Verify Analytics Tables
-- ============================================================

SELECT
    'dim_patient' AS table_name,
    COUNT(*) AS row_count
FROM dim_patient

UNION ALL

SELECT
    'dim_admission',
    COUNT(*)
FROM dim_admission

UNION ALL

SELECT
    'dim_diagnosis',
    COUNT(*)
FROM dim_diagnosis

UNION ALL

SELECT
    'dim_readmission',
    COUNT(*)
FROM dim_readmission

UNION ALL

SELECT
    'fact_encounter',
    COUNT(*)
FROM fact_encounter

ORDER BY table_name;