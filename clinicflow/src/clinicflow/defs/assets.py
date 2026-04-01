"""Dagster assets for the Charite Clinical Analytics Pipeline.

Students implement the TODO stubs to build the complete asset graph:

    raw_patients ──────────────┐
                               │
    raw_visits ────────────────┼──> patient_summaries
      │                        │
      ├──> readmission_flags ──┘
      │           │
    raw_diagnoses ┼──> department_metrics
                  │
    raw_prescriptions ──> (patient_summaries)

All data is synthetic/fictional. No real PHI is used.

German: Dagster-Assets fuer die klinische Analyse-Pipeline der Charite.

Studierende implementieren die TODO-Stubs, um den vollstaendigen
Asset-Graphen zu erstellen. Alle Daten sind synthetisch/fiktiv.
Es werden keine echten Patientendaten (PHI) verwendet.
"""

import csv  # noqa: F401 -- used by students when implementing TODO stubs
from datetime import datetime
from pathlib import Path

import dagster as dg

from clinicflow.defs.resources import PostgresResource

# ---------------------------------------------------------------------------
# Helper: locate the data/ directory (two levels up from this file)
# DE: Hilfsfunktion: das data/-Verzeichnis lokalisieren (zwei Ebenen ueber dieser Datei)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[4] / "data"


# ---------------------------------------------------------------------------
# Pure helper functions (tested independently)
# DE: Reine Hilfsfunktionen (unabhaengig getestet)
# ---------------------------------------------------------------------------


def detect_readmissions(
    visits: list[dict],
    window_days: int = 30,
) -> list[dict]:
    """Detect readmissions within a configurable window.

    Given a list of visit dicts sorted by patient_id and admission_date,
    return a list of readmission flag dicts for any pair of consecutive
    visits by the same patient where the second admission is within
    window_days of the first discharge.

    Args:
        visits: List of dicts with keys: visit_id, patient_id,
                department, admission_date, discharge_date
                (dates as datetime.date or datetime objects)
        window_days: Maximum days between discharge and next admission
                     to count as a readmission (default 30)

    Returns:
        List of dicts with keys: patient_id, original_visit_id,
        readmission_visit_id, days_between, department

    DE: Wiederaufnahmen innerhalb eines konfigurierbaren Zeitfensters erkennen.

    Erhaelt eine Liste von Besuchs-Dicts, sortiert nach Patienten-ID und Aufnahmedatum,
    und gibt eine Liste von Wiederaufnahme-Flags fuer aufeinanderfolgende Besuche
    desselben Patienten zurueck, bei denen die zweite Aufnahme innerhalb von
    window_days nach der ersten Entlassung liegt.
    """
    # TODO: Implement this function (Task 3)
    # TODO (DE): Implementiere diese Funktion (Aufgabe 3)
    # Hint:
    #   flags = []
    #   Sort visits by patient_id, then admission_date
    #   Iterate through consecutive pairs for the same patient
    #   If days between previous discharge and current admission <= window_days:
    #       append a flag dict
    #   return flags
    raise NotImplementedError("TODO: Implement detect_readmissions()")


def calculate_avg_stay(
    admission_date: datetime,
    discharge_date: datetime,
) -> float:
    """Calculate length of stay in days.

    Args:
        admission_date: Date of admission
        discharge_date: Date of discharge

    Returns:
        Number of days as a float (discharge - admission).days
        Returns 0.0 if discharge_date is None or before admission_date.

    DE: Berechnet die Aufenthaltsdauer in Tagen.

    Gibt die Anzahl der Tage als Float zurueck (Entlassung - Aufnahme).days.
    Gibt 0.0 zurueck, wenn das Entlassungsdatum None oder vor dem Aufnahmedatum liegt.
    """
    # TODO: Implement this function (Task 4)
    # TODO (DE): Implementiere diese Funktion (Aufgabe 4)
    raise NotImplementedError("TODO: Implement calculate_avg_stay()")


# ---------------------------------------------------------------------------
# Raw ingestion assets (L3 Apply)
# DE: Rohdaten-Aufnahme-Assets (L3 Anwenden)
# ---------------------------------------------------------------------------


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_patients(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load patients.csv into the patients table.

    Steps:
        1. Read data/patients.csv with csv.DictReader
        2. Use postgres.load_rows() to insert into 'patients' table
        3. Return MaterializeResult with row_count metadata

    DE: Laedt patients.csv in die Patienten-Tabelle.
    """
    # TODO: Implement this asset (Task 2)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 2)
    # Hint:
    #   with open(DATA_DIR / "patients.csv", newline="") as f:
    #       rows = list(csv.DictReader(f))
    #   count = postgres.load_rows(rows, "patients")
    #   context.log.info(f"Loaded {count} patients")
    #   return dg.MaterializeResult(metadata={"row_count": count})
    raise NotImplementedError("TODO: Implement raw_patients asset")


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_visits(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load visits.csv into the visits table.

    Steps:
        1. Read data/visits.csv with csv.DictReader
        2. Use postgres.load_rows() to insert into 'visits' table
        3. Return MaterializeResult with row_count metadata

    DE: Laedt visits.csv in die Besuche-Tabelle.
    """
    # TODO: Implement this asset (Task 2)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 2)
    raise NotImplementedError("TODO: Implement raw_visits asset")


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_diagnoses(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load diagnoses.csv into the diagnoses table.

    Steps:
        1. Read data/diagnoses.csv with csv.DictReader
        2. Use postgres.load_rows() to insert into 'diagnoses' table
        3. Return MaterializeResult with row_count metadata

    DE: Laedt diagnoses.csv in die Diagnose-Tabelle.
    """
    # TODO: Implement this asset (Task 2)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 2)
    raise NotImplementedError("TODO: Implement raw_diagnoses asset")


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_prescriptions(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load prescriptions.csv into the prescriptions table.

    Steps:
        1. Read data/prescriptions.csv with csv.DictReader
        2. Use postgres.load_rows() to insert into 'prescriptions' table
        3. Return MaterializeResult with row_count metadata

    DE: Laedt prescriptions.csv in die Verschreibungs-Tabelle.
    """
    # TODO: Implement this asset (Task 2)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 2)
    raise NotImplementedError("TODO: Implement raw_prescriptions asset")


# ---------------------------------------------------------------------------
# Readmission flags (L5 Evaluate)
# DE: Wiederaufnahme-Flags (L5 Bewerten)
# ---------------------------------------------------------------------------


@dg.asset(
    deps=[raw_visits],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def readmission_flags(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Flag patients readmitted within a configurable window (default 30 days).

    This asset depends on raw_visits.

    Steps:
        1. Query all completed visits ordered by patient_id, admission_date
        2. Use detect_readmissions() helper with the configured window
        3. Insert flags into readmission_flags table
        4. Return MaterializeResult with flag_count metadata

    Configuration:
        The readmission window (in days) can be configured. Default is 30.

    DE: Patienten markieren, die innerhalb eines konfigurierbaren Zeitfensters
    (Standard 30 Tage) wieder aufgenommen wurden. Dieses Asset haengt von raw_visits ab.
    """
    # TODO: Implement this asset (Task 3)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 3)
    # Hint:
    #   visits = postgres.execute_query(
    #       "SELECT visit_id, patient_id, department, admission_date, "
    #       "discharge_date FROM visits WHERE status = 'completed' "
    #       "ORDER BY patient_id, admission_date"
    #   )
    #   Convert rows to list of dicts
    #   flags = detect_readmissions(visit_dicts, window_days=30)
    #   Insert flags into readmission_flags table
    raise NotImplementedError("TODO: Implement readmission_flags asset")


# ---------------------------------------------------------------------------
# Patient summaries (L4 Analyze)
# DE: Patientenzusammenfassungen (L4 Analysieren)
# ---------------------------------------------------------------------------


@dg.asset(
    deps=[raw_patients, raw_visits, raw_prescriptions],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def patient_summaries(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Aggregate per-patient statistics.

    Depends on raw_patients, raw_visits, and raw_prescriptions.

    Computes for each patient:
        - total_visits: count of all visits
        - last_visit_date: most recent admission date
        - primary_department: department with most visits
        - avg_stay_days: average length of stay across all visits
        - active_prescriptions: count of prescriptions with no end_date
          or end_date in the future
        - risk_category: 'high' if total_visits >= 5 or has readmission,
                         'medium' if total_visits >= 3,
                         'low' otherwise

    Steps:
        1. Query patients, visits, and prescriptions from PostgreSQL
        2. Compute aggregations using plain Python (list comprehensions, dicts) or SQL
        3. Insert results into patient_summaries table
        4. Return MaterializeResult with patient_count metadata

    DE: Aggregierte Statistiken pro Patient berechnen.

    Berechnet fuer jeden Patienten: Gesamtbesuche, letztes Besuchsdatum,
    Hauptabteilung, durchschnittliche Aufenthaltsdauer, aktive Verschreibungen
    und Risikokategorie.
    """
    # TODO: Implement this asset (Task 4)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 4)
    raise NotImplementedError("TODO: Implement patient_summaries asset")


# ---------------------------------------------------------------------------
# Department metrics (L5 Evaluate)
# DE: Abteilungskennzahlen (L5 Bewerten)
# ---------------------------------------------------------------------------


@dg.asset(
    deps=[raw_visits, raw_diagnoses, readmission_flags],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def department_metrics(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Calculate per-department performance KPIs.

    Depends on raw_visits, raw_diagnoses, and readmission_flags.

    Computes for each department:
        - total_admissions: count of visits
        - avg_stay_days: average length of stay
        - readmission_count: number of readmission flags
        - readmission_rate: readmission_count / total_admissions
        - top_diagnosis_code: most frequent diagnosis code
        - bed_utilization_rate: placeholder (set to 0.75 or compute if desired)
        - reporting_period: current year-month or 'all-time'

    Steps:
        1. Query visits, diagnoses, and readmission_flags
        2. Group by department and compute metrics
        3. Insert into department_metrics table
        4. Return MaterializeResult with department_count metadata

    DE: Leistungskennzahlen (KPIs) pro Abteilung berechnen.

    Berechnet fuer jede Abteilung: Gesamtaufnahmen, durchschnittliche
    Aufenthaltsdauer, Wiederaufnahmeanzahl, Wiederaufnahmerate,
    haeufigster Diagnosecode und Bettenauslastungsrate.
    """
    # TODO: Implement this asset (Task 5)
    # TODO (DE): Implementiere dieses Asset (Aufgabe 5)
    raise NotImplementedError("TODO: Implement department_metrics asset")
