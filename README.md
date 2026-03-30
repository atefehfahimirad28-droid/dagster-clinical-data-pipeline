# Capstone: Clinical Analytics Pipeline

## User Stories

See [USER_STORIES.md](USER_STORIES.md) for the full list of user stories driving this project.

## Overview

A mid-sized hospital network (**ClinicFlow Health**) needs a weekly clinical analytics
pipeline to support quality improvement and regulatory reporting. The data engineering
team must build an automated pipeline that:

1. **Ingests** raw clinical data from CSV exports (patients, visits, diagnoses,
   prescriptions)
2. **Transforms** the data into actionable analytics: patient summaries, department
   performance metrics, and readmission risk flags
3. **Loads** results into PostgreSQL for downstream dashboards and reports
4. Runs on a **weekly schedule** with proper error handling and configuration

All patient data in this project is **synthetic and fictional**. No real protected
health information (PHI) is used.

## Architecture

```
 CSV Files                  Dagster Assets                    PostgreSQL
 (data/)                    (clinicflow)                      (clinicflow DB)

 patients.csv ──> [ raw_patients ] ─────────┐
                                            ├──> [ patient_summaries ] ──> patient_summaries
 visits.csv ───> [ raw_visits ] ────────────┤
                        │                   │
                        ├──> [ readmission_flags ] ──────> readmission_flags
                        │           │
 diagnoses.csv > [ raw_diagnoses ] ─┼───────┴──> [ department_metrics ] ──> department_metrics
                                    │
 prescriptions  [ raw_prescriptions ]
   .csv ──────>         │
                        └────────────────────> (used by patient_summaries)


 Schedule: weekly_analytics_schedule (Mondays 07:00)
 Jobs:     weekly_analytics_job, readmission_screening_job
```

## Asset Dependency Graph

```
raw_patients ──────────────┐
                           │
raw_visits ────────────────┼──> patient_summaries
  │                        │
  ├──> readmission_flags ──┘
  │           │
raw_diagnoses ┼──> department_metrics
              │
raw_prescriptions ──> (patient_summaries)
```

## Learning Objectives (Bloom's Taxonomy)

| Level | Verb | Objective |
|-------|------|-----------|
| L2 Understand | Explain | Describe how Dagster assets form a dependency graph |
| L3 Apply | Implement | Load CSV data into PostgreSQL using Dagster assets and resources |
| L4 Analyze | Aggregate | Compute patient summaries by combining multiple data sources |
| L5 Evaluate | Assess | Calculate readmission rates and flag at-risk patients |
| L5 Evaluate | Judge | Derive department KPIs to evaluate clinical performance |
| L6 Create | Design | Wire jobs, schedules, and configuration into a complete pipeline |

## Prerequisites

- Dagster fundamentals: assets, dependencies, I/O, jobs, error handling (Days 1-3)
- Schedules, sensors, partitions, configuration (Days 4-5)
- Python, SQL basics
- Docker

## Setup Instructions

### 1. Start infrastructure

```bash
cd capstone-medical
docker compose up -d
```

This starts PostgreSQL 17 with the `clinicflow` database and schema pre-created.

### 2. Install dependencies

```bash
cd clinicflow
uv sync --dev
```

### 3. Run tests (TDD)

```bash
uv run pytest tests/ -v
```

All tests will initially fail. Your job is to make them pass by implementing the TODO
stubs.

### 4. Start Dagster dev server

```bash
dg dev
```

Open [http://localhost:3000](http://localhost:3000) to view the Dagit UI.

## Task Breakdown

Work through the TODOs in this order. Run `uv run pytest tests/ -v` after each task
to verify your progress.

### Task 1: Configure the PostgreSQL Resource (L3)
**File:** `src/clinicflow/defs/resources.py`

Implement the `PostgresResource` methods:
- `get_connection()` -- return a psycopg2 connection
- `execute_query(query, params)` -- execute a SQL statement
- `load_rows(rows, table_name)` -- bulk-insert a list of dicts

### Task 2: Implement Raw Ingestion Assets (L3)
**File:** `src/clinicflow/defs/assets.py`

Implement the four `raw_*` assets. Each should:
- Read its CSV file with `csv.DictReader`
- Insert rows into the corresponding PostgreSQL table
- Return metadata (row count)

### Task 3: Implement Readmission Flags (L5)
**File:** `src/clinicflow/defs/assets.py`

Implement `readmission_flags`:
- Query visits ordered by patient and admission date
- Flag pairs where a patient was readmitted within the configurable window
  (default: 30 days)
- Insert flags into `readmission_flags` table

### Task 4: Implement Patient Summaries (L4)
**File:** `src/clinicflow/defs/assets.py`

Implement `patient_summaries`:
- Aggregate per-patient: total visits, average stay duration, last visit,
  primary department, active prescriptions count
- Assign risk category based on visit frequency and readmission history

### Task 5: Implement Department Metrics (L5)
**File:** `src/clinicflow/defs/assets.py`

Implement `department_metrics`:
- Group visits by department
- Calculate: total admissions, average length of stay, readmission count/rate,
  top diagnosis code
- Insert into `department_metrics` table

### Task 6: Configure Job and Schedule (L6)
**File:** `src/clinicflow/defs/jobs.py` and `src/clinicflow/defs/schedules.py`

- Define `weekly_analytics_job` selecting all assets
- Define `readmission_screening_job` for readmission + patient summary assets
- Create a weekly schedule running every Monday at 07:00

## Definition of Done

Your work is considered complete when:

1. All tests pass (`uv run pytest tests/ -v`)
2. Code is merged to the `main` branch
3. CI checks pass (conventional commits + ruff linting)

### Branching Strategy

Keep it simple -- create **one feature branch**, do your work there, then
open a Pull Request to merge into `main`:

```bash
git checkout -b feature/postgres-resource   # create your feature branch
# ... implement, commit, push ...
git push -u origin feature/postgres-resource  # push to GitHub
# Open a PR on GitHub -> merge when CI is green
```

Example branch names: `feature/postgres-resource`, `feature/raw-ingestion`,
`feature/readmission-flags`, `feature/department-metrics`.

## Expected Deliverables

1. All tests passing (`uv run pytest tests/ -v`)
2. Complete asset graph visible in Dagit UI
3. Successful materialization of all assets against the Docker PostgreSQL
4. Weekly schedule registered and visible in Dagit

## Success Criteria

| Criterion | Weight |
|-----------|--------|
| All 12 tests pass | 30% |
| Assets materialize without errors in Dagit | 25% |
| Correct asset dependencies (graph structure) | 15% |
| Readmission detection logic is correct | 15% |
| Schedule and jobs properly configured | 10% |
| Code quality (error handling, logging, docstrings) | 5% |

## Data Privacy Notice

All patient names, medical data, and clinical records in this project are
**entirely fictional and synthetically generated** for educational purposes.
No real protected health information (PHI) is used. This project is not
HIPAA-regulated as it contains no real patient data.

## AWS Deployment (Optional)

For students familiar with AWS, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for a
step-by-step guide to deploying this pipeline on EC2 + RDS using the AWS Free Tier.
