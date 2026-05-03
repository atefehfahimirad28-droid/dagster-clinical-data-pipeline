# Clinical Analytics Pipeline (Dagster)

## Overview

Production-style data pipeline built with Dagster to process **synthetic clinical data** and generate weekly analytics.

The system ingests CSV extracts (patients, visits, diagnoses, prescriptions), transforms them into analytical datasets, and loads results into PostgreSQL for reporting and dashboards.

> All data is synthetic (fictional). No real patient data (PHI) is used.

---

## What This Project Demonstrates

* Asset-based data orchestration with Dagster
* End-to-end pipeline design (ingest → transform → load)
* Data modeling for analytics (patient summaries, KPIs)
* CI/CD basics (linting, formatting, commit standards)
* Team collaboration using Git workflows

---

## Architecture

**Ingestion (raw assets)**

* `raw_patients`
* `raw_visits`
* `raw_diagnoses`
* `raw_prescriptions`

**Transformations**

* `patient_summaries`
* `readmission_flags`
* `department_metrics`

**Flow**

```
CSV → Dagster Assets → PostgreSQL
```

Scheduled execution:

* Weekly analytics job (Monday 07:00)

---

## Tech Stack

* Python
* Dagster
* PostgreSQL
* Docker
* Pytest
* Ruff (lint & format)

---

## My Contribution

This was a **group project**. My contributions include:

* Worked with Dagster asset graph and dependencies
* Contributed to transformation logic and pipeline flow
* Debugged pipeline execution and test failures
* Fixed CI issues (formatting, GitHub Actions)
* Collaborated using Git (commits, merges, workflow)

---

## How to Run

```bash
docker compose up -d
cd clinicflow
uv sync
uv run pytest tests/ -v
dg dev
```

Open Dagster UI:
http://localhost:3000

---

## Key Outputs

* Patient-level summaries
* Department performance metrics
* Readmission risk flags

---

## Project Context

Developed as part of a data engineering training program.
Focus: real-world pipeline structure, orchestration, and testing.

---

## Disclaimer

This project references Charité – Universitätsmedizin Berlin for learning context only.
No real systems or data are used.
