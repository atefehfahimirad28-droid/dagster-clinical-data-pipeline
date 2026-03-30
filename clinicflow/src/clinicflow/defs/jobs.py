"""Dagster jobs for the Charite Clinical Analytics Pipeline.

Students wire up asset jobs that select the appropriate assets for
different pipeline use cases.

German: Dagster-Jobs fuer die klinische Analyse-Pipeline der Charite.

Studierende verknuepfen Asset-Jobs, die die passenden Assets fuer
verschiedene Pipeline-Anwendungsfaelle auswaehlen.
"""

import dagster as dg

from clinicflow.defs.assets import (
    department_metrics,
    patient_summaries,
    raw_diagnoses,
    raw_patients,
    raw_prescriptions,
    raw_visits,
    readmission_flags,
)

# ---------------------------------------------------------------------------
# Job 1: Weekly full analytics pipeline (all assets)
# DE: Job 1: Woechentliche vollstaendige Analyse-Pipeline (alle Assets)
# ---------------------------------------------------------------------------

weekly_analytics_job = dg.define_asset_job(
    name="weekly_analytics_job",
    selection=[
        raw_patients,
        raw_visits,
        raw_diagnoses,
        raw_prescriptions,
        readmission_flags,
        patient_summaries,
        department_metrics,
    ],
    description="Weekly job that runs the full clinical analytics pipeline: "
    "ingest raw data, compute readmission flags, patient summaries, "
    "and department metrics.",
)


# ---------------------------------------------------------------------------
# Job 2: Readmission screening (subset of assets)
# DE: Job 2: Wiederaufnahme-Screening (Teilmenge der Assets)
# ---------------------------------------------------------------------------

readmission_screening_job = dg.define_asset_job(
    name="readmission_screening_job",
    selection=[
        raw_visits,
        readmission_flags,
        patient_summaries,
    ],
    description="Focused job that refreshes visit data, detects readmissions, "
    "and updates patient summaries with risk categories.",
)
