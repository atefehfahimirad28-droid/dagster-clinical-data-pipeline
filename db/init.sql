-- Charite Clinical Analytics Pipeline Schema
-- All data is synthetic/fictional for educational purposes.

CREATE TABLE IF NOT EXISTS patients (
    patient_id      VARCHAR(20) PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    date_of_birth   DATE NOT NULL,
    gender          VARCHAR(10) NOT NULL,
    blood_type      VARCHAR(5),
    insurance_type  VARCHAR(30),
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visits (
    visit_id            VARCHAR(20) PRIMARY KEY,
    patient_id          VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    department          VARCHAR(50) NOT NULL,
    admission_date      DATE NOT NULL,
    discharge_date      DATE,
    diagnosis_code      VARCHAR(10),
    attending_physician VARCHAR(100),
    visit_type          VARCHAR(20) NOT NULL,
    status              VARCHAR(20) DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_code  VARCHAR(10) PRIMARY KEY,
    description     VARCHAR(200) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    severity_level  INTEGER NOT NULL CHECK (severity_level BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id     VARCHAR(20) PRIMARY KEY,
    visit_id            VARCHAR(20) NOT NULL REFERENCES visits(visit_id),
    patient_id          VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    medication_name     VARCHAR(100) NOT NULL,
    dosage              VARCHAR(50) NOT NULL,
    frequency           VARCHAR(50) NOT NULL,
    start_date          DATE NOT NULL,
    end_date            DATE,
    prescribing_physician VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS patient_summaries (
    patient_id          VARCHAR(20) PRIMARY KEY REFERENCES patients(patient_id),
    total_visits        INTEGER NOT NULL,
    last_visit_date     DATE,
    primary_department  VARCHAR(50),
    avg_stay_days       NUMERIC(5,2),
    active_prescriptions INTEGER DEFAULT 0,
    risk_category       VARCHAR(20) NOT NULL,
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS department_metrics (
    department          VARCHAR(50) NOT NULL,
    reporting_period    VARCHAR(20) NOT NULL,
    total_admissions    INTEGER NOT NULL,
    avg_stay_days       NUMERIC(5,2),
    readmission_count   INTEGER DEFAULT 0,
    readmission_rate    NUMERIC(5,4),
    top_diagnosis_code  VARCHAR(10),
    bed_utilization_rate NUMERIC(5,4),
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (department, reporting_period)
);

CREATE TABLE IF NOT EXISTS readmission_flags (
    flag_id             SERIAL PRIMARY KEY,
    patient_id          VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    original_visit_id   VARCHAR(20) NOT NULL REFERENCES visits(visit_id),
    readmission_visit_id VARCHAR(20) NOT NULL REFERENCES visits(visit_id),
    days_between        INTEGER NOT NULL,
    department          VARCHAR(50),
    flagged_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
