"""Dagster definitions entry point for Charite Clinical Analytics Pipeline."""

from dagster import Definitions

from clinicflow.defs.assets import (
    department_metrics,
    patient_summaries,
    raw_diagnoses,
    raw_patients,
    raw_prescriptions,
    raw_visits,
    readmission_flags,
)
from clinicflow.defs.jobs import readmission_screening_job, weekly_analytics_job
from clinicflow.defs.resources import PostgresResource
from clinicflow.defs.schedules import weekly_analytics_schedule

defs = Definitions(
    assets=[
        raw_patients,
        raw_visits,
        raw_diagnoses,
        raw_prescriptions,
        readmission_flags,
        patient_summaries,
        department_metrics,
    ],
    jobs=[weekly_analytics_job, readmission_screening_job],
    schedules=[weekly_analytics_schedule],
    resources={"postgres": PostgresResource()},
)
