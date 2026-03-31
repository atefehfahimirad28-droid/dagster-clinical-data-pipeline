# User Stories -- Clinical Analytics Pipeline (ClinicFlow)

**Project:** Capstone Medical -- Clinical Analytics Pipeline
**Client:** Charite -- Universitaetsmedizin Berlin (educational context)
**Team:** Junior Data Engineers (group project)
**Technology:** Dagster, PostgreSQL, Docker, Python, psycopg2

> **Data Privacy Notice:** All patient data in this project is entirely synthetic and fictional. No real protected health information (PHI) is used. The reference to Charite is for educational context only.

---

## Agile Workflow Expectations

This project follows an agile workflow. Each team is expected to:

- **Sprint Planning (Day 1 of each sprint):** Review the backlog, select user stories for the sprint, assign story owners, and break stories into tasks if needed.
- **Daily Standups (15 min max):** Each team member answers: What did I do yesterday? What will I do today? Are there any blockers?
- **Sprint Review (last day of each sprint):** Demo completed work to the instructor/stakeholders. Show working software (Dagit UI, passing tests, CI pipeline).
- **Sprint Retrospective (after review):** Discuss what went well, what could improve, and agree on one concrete action item for the next sprint.

Use a project board (GitHub Projects, Trello, or similar) to track story status: **To Do**, **In Progress**, **In Review**, **Done**.

---

## Suggested Sprint Plan

Sprints are hourly blocks over a 2-day period. Each sprint includes a brief standup, focused work, and a quick review.

### Day 1

| Sprint   | Duration | Epics / Stories         | Focus                                    |
|----------|----------|-------------------------|------------------------------------------|
| Sprint 1 | 1 hour   | Epic 1: US-01           | Implement `PostgresResource` (`get_connection`, `execute_query`, `load_rows`) |
| Sprint 2 | 1 hour   | Epic 2: US-02, US-03    | Raw ingestion: `raw_patients`, `raw_visits` |
| Sprint 3 | 1 hour   | Epic 2: US-04, US-05    | Raw ingestion: `raw_diagnoses`, `raw_prescriptions` |
| Sprint 4 | 1 hour   | Epic 3: US-07           | `detect_readmissions()` helper + `readmission_flags` asset |
| Sprint 5 | 1 hour   | Epic 3: US-06           | `calculate_avg_stay()` helper + `patient_summaries` asset |

### Day 2

| Sprint   | Duration | Epics / Stories         | Focus                                    |
|----------|----------|-------------------------|------------------------------------------|
| Sprint 6 | 1 hour   | Epic 3: US-08           | `department_metrics` asset               |
| Sprint 7 | 1 hour   | Epic 4: US-09, US-10    | Jobs, schedule, end-to-end verification  |
| Sprint 8 | 1 hour   | Epic 5: US-11, US-12    | Architecture decision records + demo prep |
| Sprint 9 | 1 hour   | Epic 6--7: US-13--US-15 | Advanced / extension stories (optional)  |

---

## Definition of Done

A user story is considered **Done** when all of the following are met:

- [ ] All acceptance criteria are satisfied
- [ ] Relevant unit/integration tests pass (`uv run pytest tests/ -v`)
- [ ] Code has been reviewed by at least one other team member (PR approved)
- [ ] CI pipeline is green (lint + tests pass on the PR)
- [ ] Code is merged into the `main` branch
- [ ] Any new functionality is documented (docstrings, comments where needed)

---

## Branching Strategy

```
main                          (protected -- merge only via PR)
  ├── feature/US-01-postgres-resource
  ├── feature/US-02-raw-patients
  ├── feature/US-06-patient-summaries
  └── ...
```

- **`main`**: Always stable and deployable. Protected -- no direct pushes.
- **`feature/US-XX-short-description`**: One branch per user story. Create from `main`, merge back into `main` via pull request.

Rules:
1. Never push directly to `main`.
2. Every merge requires a pull request with CI passing.
3. Delete feature branches after merging.

---

## Patient Privacy Considerations

- All data files (`data/*.csv`) contain **synthetic, computer-generated records**. No real patient data is used at any point.
- Even with synthetic data, treat the project as if it were real: do not commit credentials, do not expose database ports publicly, use `.env` files for secrets and add them to `.gitignore`.
- In architecture decision records (US-11), discuss what data privacy measures would be required for a real clinical data pipeline (e.g., GDPR, HIPAA, anonymization, access control, audit logging).

---

## Epic 1: Resources

### US-01: Implement PostgresResource

**As a** data engineer,
**I want** a reusable Dagster resource for PostgreSQL operations,
**So that** all assets can interact with the database through a consistent interface.

**Acceptance Criteria:**
- [ ] `PostgresResource` class is implemented in `src/clinicflow/defs/resources.py`
- [ ] `get_connection()` returns a valid `psycopg2` connection to the clinicflow database
- [ ] `execute_query(query, params)` executes a SQL statement and returns results for SELECT queries
- [ ] `load_rows(rows, table_name)` bulk-inserts a list of dicts into the specified table and returns the row count
- [ ] Connections are properly closed after use (context manager or explicit close)
- [ ] Unit tests for the resource methods pass

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** Backend Developer

---

## Epic 2: Data Ingestion (Raw Assets)

### US-02: Implement raw_patients Asset

**As a** data engineer,
**I want** a Dagster asset that loads `patients.csv` into PostgreSQL,
**So that** patient data is available for downstream analytics.

**Acceptance Criteria:**
- [ ] `raw_patients` asset reads `data/patients.csv` using `csv.DictReader`
- [ ] Data is inserted into the `patients` table via `postgres.load_rows()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded patients
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A

---

### US-03: Implement raw_visits Asset

**As a** data engineer,
**I want** a Dagster asset that loads `visits.csv` into PostgreSQL,
**So that** visit data is available for readmission detection and department metrics.

**Acceptance Criteria:**
- [ ] `raw_visits` asset reads `data/visits.csv` using `csv.DictReader`
- [ ] Data is inserted into the `visits` table via `postgres.load_rows()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded visits
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer B

---

### US-04: Implement raw_diagnoses Asset

**As a** data engineer,
**I want** a Dagster asset that loads `diagnoses.csv` into PostgreSQL,
**So that** diagnosis data is available for department metrics and analytics.

**Acceptance Criteria:**
- [ ] `raw_diagnoses` asset reads `data/diagnoses.csv` using `csv.DictReader`
- [ ] Data is inserted into the `diagnoses` table via `postgres.load_rows()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded diagnoses
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A

---

### US-05: Implement raw_prescriptions Asset

**As a** data engineer,
**I want** a Dagster asset that loads `prescriptions.csv` into PostgreSQL,
**So that** prescription data is available for patient summary calculations.

**Acceptance Criteria:**
- [ ] `raw_prescriptions` asset reads `data/prescriptions.csv` using `csv.DictReader`
- [ ] Data is inserted into the `prescriptions` table via `postgres.load_rows()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded prescriptions
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer B

---

## Epic 3: Clinical Transformations

### US-06: Implement patient_summaries Asset

**As a** clinical data analyst,
**I want** per-patient summary statistics aggregated from multiple data sources,
**So that** clinicians can quickly assess each patient's clinical profile and risk level.

**Acceptance Criteria:**
- [ ] Asset depends on `raw_patients`, `raw_visits`, and `raw_prescriptions`
- [ ] Computes per patient: `total_visits`, `avg_stay_days`, `last_visit_date`, `primary_department`, `active_prescriptions` count
- [ ] Assigns `risk_category`: "high" if total_visits >= 5 or patient has readmission, "medium" if total_visits >= 3, "low" otherwise
- [ ] Results are inserted into the `patient_summaries` table
- [ ] Asset returns `MaterializeResult` with `patient_count` metadata
- [ ] The `calculate_avg_stay()` helper function is implemented and tested
- [ ] Asset belongs to the `analytics` group
- [ ] Corresponding tests pass

**Story Points:** 5 (large)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A + B (pair programming recommended)

---

### US-07: Implement readmission_flags Asset

**As a** quality management officer,
**I want** patients readmitted within a configurable window (default 30 days) to be flagged,
**So that** the hospital can identify and investigate potentially preventable readmissions.

**Acceptance Criteria:**
- [ ] Asset depends on `raw_visits`
- [ ] Queries all completed visits ordered by `patient_id` and `admission_date`
- [ ] Uses the `detect_readmissions()` helper function to identify readmissions within the configured window
- [ ] `detect_readmissions()` returns dicts with: `patient_id`, `original_visit_id`, `readmission_visit_id`, `days_between`, `department`
- [ ] Readmission flags are inserted into the `readmission_flags` table
- [ ] Asset returns `MaterializeResult` with `flag_count` metadata
- [ ] The readmission window is configurable (default 30 days)
- [ ] Asset belongs to the `analytics` group
- [ ] Corresponding tests pass

**Story Points:** 5 (large)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer B

---

### US-08: Implement department_metrics Asset

**As a** department head,
**I want** per-department performance KPIs calculated from visit and diagnosis data,
**So that** I can evaluate my department's clinical performance and identify improvement areas.

**Acceptance Criteria:**
- [ ] Asset depends on `raw_visits`, `raw_diagnoses`, and `readmission_flags`
- [ ] Computes per department: `total_admissions`, `avg_stay_days`, `readmission_count`, `readmission_rate`, `top_diagnosis_code`
- [ ] `readmission_rate` is calculated as `readmission_count / total_admissions`
- [ ] `bed_utilization_rate` is set to a placeholder value (0.75) or computed if desired
- [ ] `reporting_period` is set to current year-month or "all-time"
- [ ] Results are inserted into the `department_metrics` table
- [ ] Asset returns `MaterializeResult` with `department_count` metadata
- [ ] Asset belongs to the `analytics` group
- [ ] Corresponding tests pass

**Story Points:** 5 (large)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A

---

## Epic 4: Orchestration

### US-09: Implement weekly_analytics_schedule

**As a** data platform operator,
**I want** the analytics pipeline to run automatically every Monday at 07:00,
**So that** clinical reports are refreshed weekly without manual intervention.

**Acceptance Criteria:**
- [ ] `weekly_analytics_job` is defined in `src/clinicflow/defs/jobs.py` and selects all assets
- [ ] `readmission_screening_job` is defined and selects only readmission + patient summary assets
- [ ] `weekly_analytics_schedule` is defined in `src/clinicflow/defs/schedules.py`
- [ ] Schedule triggers `weekly_analytics_job` with a cron expression for every Monday at 07:00 (`0 7 * * 1`)
- [ ] Schedule is visible and registered in the Dagit UI
- [ ] Corresponding tests pass

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A or B

---

### US-10: End-to-End Pipeline Test in Dagit

**As a** team,
**I want** to verify that the entire pipeline works end-to-end in Dagit,
**So that** we can confidently demo and deliver a working system.

**Acceptance Criteria:**
- [ ] All assets can be materialized in sequence from the Dagit UI without errors
- [ ] Asset graph in Dagit shows the correct dependency structure matching the architecture diagram
- [ ] `patient_summaries` table contains aggregated data after materialization
- [ ] `readmission_flags` table contains flagged readmissions after materialization
- [ ] `department_metrics` table contains per-department KPIs after materialization
- [ ] All 12 tests pass (`uv run pytest tests/ -v`)
- [ ] No unhandled errors or warnings in Dagster logs

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** Full Team

---

## Epic 5: Documentation & Demo

### US-11: Write Architecture Decision Records

**As a** team,
**I want** documented architecture decisions,
**So that** future developers understand why we chose specific technologies and approaches.

**Acceptance Criteria:**
- [ ] ADR document exists (e.g., `docs/adr/` or a section in README)
- [ ] ADR-001: Why Dagster was chosen as the orchestrator (vs. Airflow, Prefect, etc.)
- [ ] ADR-002: Data privacy considerations for clinical data (GDPR, anonymization, access control, audit logging -- even though data is synthetic, discuss what would be needed for real PHI)
- [ ] ADR-003: Database schema design decisions (why these tables, normalization choices)
- [ ] Each ADR follows a consistent format: Context, Decision, Consequences
- [ ] ADRs are reviewed by the team

**Story Points:** 3 (medium)
**Priority:** Should Have
**Suggested Assignee:** Documentation Lead / All Team Members

---

### US-12: Prepare Live Demo in Dagit

**As a** team,
**I want** a polished live demo of the pipeline running in Dagit,
**So that** we can present our work to instructors and stakeholders.

**Acceptance Criteria:**
- [ ] Demo script is prepared covering: asset graph overview, materialization run, schedule configuration
- [ ] Asset graph is shown in Dagit with all groups and dependencies clearly visible
- [ ] Readmission detection is demonstrated: materialize `readmission_flags`, query results, explain the logic
- [ ] Department metrics dashboard data is shown: materialize `department_metrics`, query results from PostgreSQL
- [ ] Schedule `weekly_analytics_schedule` is shown as registered and active
- [ ] Team can answer questions about architecture decisions, error handling, and configuration
- [ ] Demo runs successfully without errors (rehearsed at least once)

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** Full Team (assign a demo lead)

---

## Summary Table

| ID    | Title                              | Points | Priority      | Epic |
|-------|------------------------------------|--------|---------------|------|
| US-01 | Implement PostgresResource         | 3      | Must Have     | 1    |
| US-02 | Implement raw_patients asset       | 2      | Must Have     | 2    |
| US-03 | Implement raw_visits asset         | 2      | Must Have     | 2    |
| US-04 | Implement raw_diagnoses asset      | 2      | Must Have     | 2    |
| US-05 | Implement raw_prescriptions asset  | 2      | Must Have     | 2    |
| US-06 | Implement patient_summaries asset  | 5      | Must Have     | 3    |
| US-07 | Implement readmission_flags asset  | 5      | Must Have     | 3    |
| US-08 | Implement department_metrics asset | 5      | Must Have     | 3    |
| US-09 | weekly_analytics_schedule          | 3      | Must Have     | 4    |
| US-10 | End-to-end pipeline test           | 3      | Must Have     | 4    |
| US-11 | Architecture decision records      | 3      | Should Have   | 5    |
| US-12 | Prepare live demo in Dagit        | 3      | Must Have     | 5    |
| **Total** |                              | **38** |               |      |

---

## Advanced / Extension Stories

> The following stories are **optional** and intended for advanced students or teams that have completed the core pipeline ahead of schedule. They are **not required** for the capstone grade.

---

### Epic 6: Advanced -- Pandas Integration (Optional)

### US-13: Refactor Ingestion to Use pandas

**As a** data engineer who is comfortable with pandas,
**I want** to replace `csv.DictReader` + `load_rows()` with pandas DataFrames,
**So that** I can leverage pandas for data validation and transformation before loading.

**Acceptance Criteria:**
- [ ] Install pandas as an optional dependency: `uv add pandas` (already available via `[project.optional-dependencies]` in `pyproject.toml`)
- [ ] Add a `load_dataframe(df, table_name)` method to `PostgresResource` that accepts a pandas DataFrame
- [ ] Refactor raw ingestion assets to use `pd.read_csv()` and `postgres.load_dataframe()`
- [ ] All existing tests still pass
- [ ] No change to the asset dependency graph or public interface

**Story Points:** 3 (medium)
**Priority:** Could Have
**Suggested Assignee:** Advanced student

---

### Epic 7: Advanced -- AWS Deployment (Optional)

> See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for the full step-by-step guide.

### US-14: Deploy Pipeline to AWS (EC2 + RDS)

**As a** data engineer familiar with AWS,
**I want** to deploy the ClinicFlow pipeline to EC2 with an RDS PostgreSQL backend,
**So that** the pipeline runs in a cloud environment similar to production.

**Acceptance Criteria:**
- [ ] An RDS PostgreSQL `db.t3.micro` instance is provisioned (Free Tier)
- [ ] The database schema (`db/init.sql`) is applied to the RDS instance
- [ ] An EC2 `t3.micro` instance is launched and configured with Python, uv, and the project
- [ ] CSV data files are uploaded to an S3 bucket
- [ ] Environment variables (DB host, credentials, S3 bucket) are configured via `.env`
- [ ] `dg dev` runs on EC2 and Dagit UI is accessible via the instance's public IP
- [ ] All assets can be materialized against the RDS database
- [ ] All resources are torn down after the demo to avoid charges

**Story Points:** 5 (large)
**Priority:** Could Have
**Suggested Assignee:** Advanced student / team with AWS experience

---

### US-15: Adapt CSV Ingestion for S3

**As a** data engineer,
**I want** the raw ingestion assets to read CSV files from S3 instead of the local filesystem,
**So that** the pipeline works in a cloud-native deployment.

**Acceptance Criteria:**
- [ ] `boto3` is added as a dependency (`uv add boto3`)
- [ ] A helper function reads CSV files from S3 using `boto3` and returns a list of dicts
- [ ] Raw ingestion assets detect whether to read from local `data/` or S3 based on an environment variable
- [ ] The pipeline works both locally (CSV files) and on AWS (S3)
- [ ] All existing tests still pass (they do not require S3 access)

**Story Points:** 3 (medium)
**Priority:** Could Have
**Suggested Assignee:** Advanced student

---

## Extended Summary Table (Including Advanced Stories)

| ID    | Title                              | Points | Priority      | Epic | Required |
|-------|------------------------------------|--------|---------------|------|----------|
| US-01 | Implement PostgresResource         | 3      | Must Have     | 1    | Yes      |
| US-02 | Implement raw_patients asset       | 2      | Must Have     | 2    | Yes      |
| US-03 | Implement raw_visits asset         | 2      | Must Have     | 2    | Yes      |
| US-04 | Implement raw_diagnoses asset      | 2      | Must Have     | 2    | Yes      |
| US-05 | Implement raw_prescriptions asset  | 2      | Must Have     | 2    | Yes      |
| US-06 | Implement patient_summaries asset  | 5      | Must Have     | 3    | Yes      |
| US-07 | Implement readmission_flags asset  | 5      | Must Have     | 3    | Yes      |
| US-08 | Implement department_metrics asset | 5      | Must Have     | 3    | Yes      |
| US-09 | weekly_analytics_schedule          | 3      | Must Have     | 4    | Yes      |
| US-10 | End-to-end pipeline test           | 3      | Must Have     | 4    | Yes      |
| US-11 | Architecture decision records      | 3      | Should Have   | 5    | Yes      |
| US-12 | Prepare live demo in Dagit        | 3      | Must Have     | 5    | Yes      |
| US-13 | Refactor ingestion to use pandas   | 3      | Could Have    | 6    | No       |
| US-14 | Deploy pipeline to AWS             | 5      | Could Have    | 7    | No       |
| US-15 | Adapt CSV ingestion for S3         | 3      | Could Have    | 7    | No       |
| **Core Total** |                         | **38** |               |      |          |
| **With Advanced** |                      | **49** |               |      |          |
