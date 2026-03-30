# User Stories -- Clinical Analytics Pipeline (ClinicFlow)

**Project:** Capstone Medical -- Clinical Analytics Pipeline
**Client:** Charite -- Universitaetsmedizin Berlin (educational context)
**Team:** Junior Data Engineers (group project)
**Technology:** Dagster, PostgreSQL, Docker, Python, pandas, psycopg2

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

| Sprint   | Duration | Epics                              | Focus                                    |
|----------|----------|------------------------------------|------------------------------------------|
| Sprint 1 | ~3 days  | Epic 1 (Project Setup & CI/CD) + Epic 2 (Infrastructure & Resources) | Foundation: repo, CI/CD, Docker, PostgresResource |
| Sprint 2 | ~4 days  | Epic 3 (Data Ingestion) + Epic 4 (Clinical Transformations)          | Core pipeline: raw assets + analytics    |
| Sprint 3 | ~3 days  | Epic 5 (Orchestration) + Epic 6 (Documentation & Demo)              | Scheduling, end-to-end test, demo prep   |

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
  ├── feature/US-01-repo-setup
  ├── feature/US-02-ci-pipeline
  ├── feature/US-07-raw-patients
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
- In architecture decision records (US-16), discuss what data privacy measures would be required for a real clinical data pipeline (e.g., GDPR, HIPAA, anonymization, access control, audit logging).

---

## Epic 1: Project Setup & CI/CD

### US-01: Repository and Branch Strategy Setup

**As a** development team,
**I want** a properly configured Git repository with a branching strategy,
**So that** we can collaborate without merge conflicts and maintain code quality.

**Acceptance Criteria:**
- [ ] GitHub repository is created and all team members have push access
- [ ] `main` branch exists and is protected (no direct pushes, require PR review)
- [ ] Branch naming convention `feature/US-XX-description` is documented and agreed upon
- [ ] `.gitignore` includes `.venv/`, `__pycache__/`, `.env`, `.dagster/`, `*.pyc`
- [ ] All team members have cloned the repo and can create feature branches

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Team Lead / DevOps

---

### US-02: CI Pipeline with GitHub Actions

**As a** development team,
**I want** an automated CI pipeline that lints and tests every pull request,
**So that** we catch errors early and maintain code quality.

**Acceptance Criteria:**
- [ ] `.github/workflows/ci.yml` exists and runs on every PR to `main`
- [ ] Pipeline installs dependencies using `uv sync --dev`
- [ ] Pipeline runs `ruff check .` for linting (zero violations required)
- [ ] Pipeline runs `uv run pytest tests/ -v` and fails if any test fails
- [ ] PR merge is blocked if CI pipeline fails (branch protection rule)
- [ ] Pipeline runs on Python 3.10+ (matching the project requirement)

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** DevOps / CI Engineer

---

### US-03: CD Pipeline for Deployment Readiness

**As a** development team,
**I want** a CD pipeline that verifies Docker builds and infrastructure health,
**So that** we know our application is deployable at all times.

**Acceptance Criteria:**
- [ ] CI/CD workflow includes a step to run `docker compose build` and verify it succeeds
- [ ] A step runs `docker compose up -d` and verifies all services reach healthy state
- [ ] PostgreSQL health check passes (connection test using `pg_isready` or similar)
- [ ] Pipeline tears down Docker resources after verification (`docker compose down`)
- [ ] Pipeline runs on the `main` branch after merge (or on a schedule)

**Story Points:** 3 (medium)
**Priority:** Should Have
**Suggested Assignee:** DevOps / CI Engineer

---

### US-04: Development Environment Setup

**As a** team member,
**I want** a working local development environment,
**So that** I can develop and test pipeline code on my machine.

**Acceptance Criteria:**
- [ ] `docker compose up -d` starts PostgreSQL with the `clinicflow` database and schema
- [ ] `uv sync --dev` installs all Python dependencies without errors
- [ ] `uv run pytest tests/ -v` runs (tests may fail, but the test runner works)
- [ ] `dg dev` starts the Dagster dev server and Dagit UI is accessible at `localhost:3000`
- [ ] Every team member has confirmed their environment works (documented in a checklist)
- [ ] A brief `SETUP.md` or section in README describes the setup steps

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** All Team Members

---

## Epic 2: Infrastructure & Resources

### US-05: PostgreSQL Database Setup

**As a** data engineer,
**I want** a PostgreSQL database running in Docker with pre-created tables,
**So that** our pipeline has a target to load data into.

**Acceptance Criteria:**
- [ ] `docker compose up -d` starts PostgreSQL 17 on port 5432
- [ ] The `clinicflow` database is created automatically
- [ ] `init.sql` creates all required tables: `patients`, `visits`, `diagnoses`, `prescriptions`, `readmission_flags`, `patient_summaries`, `department_metrics`
- [ ] Tables match the schema expected by the assets (correct column names and types)
- [ ] Database can be connected to with the credentials in `docker-compose.yml`
- [ ] Running `docker compose down -v` and `docker compose up -d` gives a clean database

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Infrastructure / Backend

---

### US-06: Implement PostgresResource

**As a** data engineer,
**I want** a reusable Dagster resource for PostgreSQL operations,
**So that** all assets can interact with the database through a consistent interface.

**Acceptance Criteria:**
- [ ] `PostgresResource` class is implemented in `src/clinicflow/defs/resources.py`
- [ ] `get_connection()` returns a valid `psycopg2` connection to the clinicflow database
- [ ] `execute_query(query, params)` executes a SQL statement and returns results for SELECT queries
- [ ] `load_dataframe(df, table_name)` bulk-inserts a pandas DataFrame into the specified table and returns the row count
- [ ] Connections are properly closed after use (context manager or explicit close)
- [ ] Unit tests for the resource methods pass

**Story Points:** 3 (medium)
**Priority:** Must Have
**Suggested Assignee:** Backend Developer

---

## Epic 3: Data Ingestion (Raw Assets)

### US-07: Implement raw_patients Asset

**As a** data engineer,
**I want** a Dagster asset that loads `patients.csv` into PostgreSQL,
**So that** patient data is available for downstream analytics.

**Acceptance Criteria:**
- [ ] `raw_patients` asset reads `data/patients.csv` using pandas
- [ ] Data is inserted into the `patients` table via `postgres.load_dataframe()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded patients
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A

---

### US-08: Implement raw_visits Asset

**As a** data engineer,
**I want** a Dagster asset that loads `visits.csv` into PostgreSQL,
**So that** visit data is available for readmission detection and department metrics.

**Acceptance Criteria:**
- [ ] `raw_visits` asset reads `data/visits.csv` using pandas
- [ ] Data is inserted into the `visits` table via `postgres.load_dataframe()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded visits
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer B

---

### US-09: Implement raw_diagnoses Asset

**As a** data engineer,
**I want** a Dagster asset that loads `diagnoses.csv` into PostgreSQL,
**So that** diagnosis data is available for department metrics and analytics.

**Acceptance Criteria:**
- [ ] `raw_diagnoses` asset reads `data/diagnoses.csv` using pandas
- [ ] Data is inserted into the `diagnoses` table via `postgres.load_dataframe()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded diagnoses
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer A

---

### US-10: Implement raw_prescriptions Asset

**As a** data engineer,
**I want** a Dagster asset that loads `prescriptions.csv` into PostgreSQL,
**So that** prescription data is available for patient summary calculations.

**Acceptance Criteria:**
- [ ] `raw_prescriptions` asset reads `data/prescriptions.csv` using pandas
- [ ] Data is inserted into the `prescriptions` table via `postgres.load_dataframe()`
- [ ] Asset returns `MaterializeResult` with `row_count` metadata
- [ ] Asset logs the number of loaded prescriptions
- [ ] Asset belongs to the `raw_ingestion` group
- [ ] Corresponding tests pass

**Story Points:** 2 (small)
**Priority:** Must Have
**Suggested Assignee:** Data Engineer B

---

## Epic 4: Clinical Transformations

### US-11: Implement patient_summaries Asset

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

### US-12: Implement readmission_flags Asset

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

### US-13: Implement department_metrics Asset

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

## Epic 5: Orchestration

### US-14: Implement weekly_analytics_schedule

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

### US-15: End-to-End Pipeline Test in Dagit

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

## Epic 6: Documentation & Demo

### US-16: Write Architecture Decision Records

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

### US-17: Prepare Live Demo in Dagit

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
| US-01 | Repository and branch strategy     | 2      | Must Have     | 1    |
| US-02 | CI pipeline with GitHub Actions    | 3      | Must Have     | 1    |
| US-03 | CD pipeline for deployment         | 3      | Should Have   | 1    |
| US-04 | Development environment setup      | 2      | Must Have     | 1    |
| US-05 | PostgreSQL database setup          | 2      | Must Have     | 2    |
| US-06 | Implement PostgresResource         | 3      | Must Have     | 2    |
| US-07 | Implement raw_patients asset       | 2      | Must Have     | 3    |
| US-08 | Implement raw_visits asset         | 2      | Must Have     | 3    |
| US-09 | Implement raw_diagnoses asset      | 2      | Must Have     | 3    |
| US-10 | Implement raw_prescriptions asset  | 2      | Must Have     | 3    |
| US-11 | Implement patient_summaries asset  | 5      | Must Have     | 4    |
| US-12 | Implement readmission_flags asset  | 5      | Must Have     | 4    |
| US-13 | Implement department_metrics asset | 5      | Must Have     | 4    |
| US-14 | weekly_analytics_schedule          | 3      | Must Have     | 5    |
| US-15 | End-to-end pipeline test           | 3      | Must Have     | 5    |
| US-16 | Architecture decision records      | 3      | Should Have   | 6    |
| US-17 | Prepare live demo in Dagit        | 3      | Must Have     | 6    |
| **Total** |                              | **50** |               |      |
