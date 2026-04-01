# ADR-003: Database Schema Design

**Status:** Accepted
**Date:** 2026-04-01

## Context

The Charite Clinical Analytics Pipeline needs a relational schema in PostgreSQL to
store clinical data ingested from CSV files and the analytics results computed by
Dagster assets. The schema must support:

- Ingestion of four source datasets: patients, visits, diagnoses, and prescriptions
- Storage of three computed analytics outputs: patient summaries, department metrics,
  and readmission flags
- Idempotent pipeline runs (re-running the pipeline produces the same result)
- Referential integrity between related entities
- Clear separation between raw source data and derived analytics

## Decision

We use a **7-table normalized schema** defined in `db/init.sql`, split into two
logical groups:

### Source tables (4 tables)

| Table            | Primary Key       | Purpose                                      |
|------------------|-------------------|----------------------------------------------|
| `patients`       | `patient_id`      | Patient demographics (name, DOB, gender, blood type, insurance) |
| `visits`         | `visit_id`        | Hospital visits with department, dates, diagnosis code, status |
| `diagnoses`      | `diagnosis_code`  | Diagnosis reference data (ICD-style codes, categories, severity) |
| `prescriptions`  | `prescription_id` | Medications linked to both a visit and a patient |

### Computed tables (3 tables)

| Table                | Primary Key                       | Purpose                                      |
|----------------------|-----------------------------------|----------------------------------------------|
| `patient_summaries`  | `patient_id`                      | Per-patient aggregations (total visits, risk category, avg stay) |
| `department_metrics` | `(department, reporting_period)`  | Per-department KPIs (admissions, readmission rate, top diagnosis) |
| `readmission_flags`  | `flag_id` (SERIAL)                | Detected readmissions within a 30-day window |

### Normalization choices

1. **Diagnoses as a separate table.** Rather than embedding diagnosis descriptions
   in every visit row, the `diagnoses` table serves as a reference/lookup table.
   Visits reference diagnosis codes via `diagnosis_code`. This avoids data
   duplication and allows diagnosis metadata (description, category, severity) to
   be maintained independently. It also supports many-to-many relationships if the
   schema is later extended with a junction table.

2. **Prescriptions linked to both visits and patients.** The `prescriptions` table
   carries foreign keys to both `visits(visit_id)` and `patients(patient_id)`. This
   denormalization is intentional: it allows efficient queries for "all prescriptions
   for a patient" without joining through the visits table, which is the common
   access pattern for the `patient_summaries` asset.

3. **Computed tables are fully separate.** The three analytics tables
   (`patient_summaries`, `department_metrics`, `readmission_flags`) are distinct
   from the source tables. This separation means:
   - Source data is never modified by analytics computation.
   - Computed tables can be dropped and rebuilt without affecting source data.
   - Different retention and access policies can apply to each group.

### Idempotent loading strategy

All assets use **TRUNCATE CASCADE + INSERT** rather than upsert (INSERT ON CONFLICT):

```python
cur.execute(
    sql.SQL("TRUNCATE TABLE {} CASCADE").format(sql.Identifier(table_name))
)
cur.executemany(insert_sql, values)
```

This approach ensures that every pipeline run produces a clean, complete result
regardless of prior state. It is simpler to reason about than upsert logic and
avoids edge cases around partial updates. The `CASCADE` option propagates the
truncation to dependent tables (e.g., truncating `visits` also clears
`readmission_flags` that reference visits), maintaining referential integrity.

### Foreign key constraints

The schema enforces referential integrity through foreign keys:

- `visits.patient_id` references `patients.patient_id`
- `prescriptions.visit_id` references `visits.visit_id`
- `prescriptions.patient_id` references `patients.patient_id`
- `patient_summaries.patient_id` references `patients.patient_id`
- `readmission_flags.patient_id` references `patients.patient_id`
- `readmission_flags.original_visit_id` references `visits.visit_id`
- `readmission_flags.readmission_visit_id` references `visits.visit_id`

These constraints prevent orphaned records and enforce data quality at the database
level -- invalid data is rejected on insert rather than discovered later during
analytics computation.

### Data type choices

- **VARCHAR for IDs** (`patient_id`, `visit_id`, etc.) rather than integers,
  because the source CSV files use string identifiers (e.g., `P001`, `V042`).
- **DATE for temporal fields** (`admission_date`, `discharge_date`, `date_of_birth`)
  since time-of-day precision is not needed for the current analytics.
- **NUMERIC(5,2) and NUMERIC(5,4)** for computed metrics (`avg_stay_days`,
  `readmission_rate`) to ensure consistent decimal precision.
- **SERIAL for `flag_id`** in `readmission_flags` because flags are generated
  (not sourced from CSV) and need a synthetic primary key.
- **CHECK constraint** on `diagnoses.severity_level` (BETWEEN 1 AND 5) to enforce
  valid severity ranges at the database level.

## Consequences

### Positive

- **Clean separation of raw and computed data.** Source tables and analytics tables
  serve distinct roles, making the pipeline easier to understand and debug.
- **Idempotent pipeline runs.** TRUNCATE + INSERT means every run produces identical
  results from the same source data, with no residual state from prior runs.
- **Schema-enforced data quality.** Foreign keys, NOT NULL constraints, and CHECK
  constraints catch data issues at insert time.
- **Extensibility.** The normalized structure allows adding new analytics tables or
  extending source tables (e.g., adding a visit-diagnosis junction table) without
  restructuring existing tables.

### Negative

- **TRUNCATE CASCADE can be destructive.** If the pipeline is interrupted between
  truncating a table and inserting new data, the table will be empty. For production,
  a transactional approach (truncate and insert within a single transaction) or a
  staging-table swap pattern would be safer. Note: the current `load_rows()`
  implementation does use a transaction via the `with conn` context manager.
- **No indexing beyond primary keys.** The current schema does not define secondary
  indexes. As data volume grows, queries filtering on `patient_id` in the visits
  table or `department` in readmission_flags would benefit from explicit indexes.
- **VARCHAR IDs prevent natural ordering.** String-based IDs like `P001` sort
  lexicographically, not numerically. This is acceptable for the current dataset
  size but could cause confusion with larger ID spaces (e.g., `P9` sorts after
  `P10`).
