-- ============================================================
-- Hospital Readmission Analytics Platform
-- Analytics Queries
-- ============================================================


-- ------------------------------------------------------------
-- 1. Total Patient Encounters
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_encounters
FROM hospital_readmissions;


-- ------------------------------------------------------------
-- 2. Readmission Distribution
-- ------------------------------------------------------------

SELECT
    readmission_status,
    COUNT(*) AS total_encounters
FROM hospital_readmissions
GROUP BY readmission_status
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 3. Overall 30-Day Readmission Rate
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions;


-- ------------------------------------------------------------
-- 4. Average Length of Hospital Stay
-- ------------------------------------------------------------

SELECT
    ROUND(
        AVG(time_in_hospital),
        2
    ) AS average_days_in_hospital
FROM hospital_readmissions;


-- ------------------------------------------------------------
-- 5. Readmission by Age Group
-- ------------------------------------------------------------

SELECT
    age,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY age
ORDER BY age;


-- ------------------------------------------------------------
-- 6. Readmission by Gender
-- ------------------------------------------------------------

SELECT
    gender,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY gender
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 7. Readmission by Race
-- ------------------------------------------------------------

SELECT
    COALESCE(race, 'Unknown') AS race,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY COALESCE(race, 'Unknown')
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 8. Readmission by Admission Type
-- ------------------------------------------------------------

SELECT
    admission_type_id,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY admission_type_id
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 9. Average Healthcare Utilization
-- ------------------------------------------------------------

SELECT
    ROUND(AVG(number_outpatient), 2) AS average_outpatient_visits,
    ROUND(AVG(number_emergency), 2) AS average_emergency_visits,
    ROUND(AVG(number_inpatient), 2) AS average_inpatient_visits
FROM hospital_readmissions;


-- ------------------------------------------------------------
-- 10. Previous Inpatient Visits and Readmission
-- ------------------------------------------------------------

SELECT
    number_inpatient,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY number_inpatient
ORDER BY number_inpatient;


-- ------------------------------------------------------------
-- 11. Diabetes Medication and Readmission
-- ------------------------------------------------------------

SELECT
    diabetes_med,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY diabetes_med
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 12. Medication Change and Readmission
-- ------------------------------------------------------------

SELECT
    medication_change,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY medication_change
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 13. A1C Result and Readmission
-- ------------------------------------------------------------

SELECT
    COALESCE(a1c_result, 'Not Tested') AS a1c_result,
    COUNT(*) AS total_encounters,

    COUNT(*) FILTER (
        WHERE readmission_status = 'Readmitted Within 30 Days'
    ) AS readmitted_within_30_days,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE readmission_status = 'Readmitted Within 30 Days'
        ) / COUNT(*),
        2
    ) AS readmission_rate_percent

FROM hospital_readmissions
GROUP BY COALESCE(a1c_result, 'Not Tested')
ORDER BY total_encounters DESC;


-- ------------------------------------------------------------
-- 14. Average Clinical Activity by Readmission Status
-- ------------------------------------------------------------

SELECT
    readmission_status,

    ROUND(
        AVG(time_in_hospital),
        2
    ) AS average_hospital_days,

    ROUND(
        AVG(num_lab_procedures),
        2
    ) AS average_lab_procedures,

    ROUND(
        AVG(num_procedures),
        2
    ) AS average_procedures,

    ROUND(
        AVG(num_medications),
        2
    ) AS average_medications,

    ROUND(
        AVG(number_diagnoses),
        2
    ) AS average_diagnoses

FROM hospital_readmissions
GROUP BY readmission_status
ORDER BY readmission_status;