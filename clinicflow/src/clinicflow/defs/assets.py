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

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import dagster as dg

from clinicflow.defs.resources import PostgresResource

# ---------------------------------------------------------------------------
# Helper: locate the data/ directory (two levels up from this file)
# DE: Hilfsfunktion: das data/-Verzeichnis lokalisieren (zwei Ebenen ueber dieser Datei)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[4] / "data"


def _load_raw_data(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
    name: str,
) -> dg.MaterializeResult:
    """Helper function to load CSV data into PostgreSQL table.

    Args:
        context: Dagster execution context
        postgres: PostgreSQL resource
        name: Name of the CSV file (without extension) and table name

    Returns:
        MaterializeResult with row_count metadata

    DE: Hilfsfunktion zum Laden von CSV-Daten in die PostgreSQL-Tabelle.
    """
    file_path = DATA_DIR / f"{name}.csv"
    with open(file_path, newline="") as f:
        rows = list(csv.DictReader(f))
    count = postgres.load_rows(rows, name)
    context.log.info(f"Loaded {count} {name}")
    return dg.MaterializeResult(metadata={"row_count": count})


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
    flags = []

    sorted_visits = sorted(
        visits,
        key=lambda v: (v["patient_id"], v["admission_date"]),
    )

    for i in range(1, len(sorted_visits)):
        prev = sorted_visits[i - 1]
        curr = sorted_visits[i]

        if prev["patient_id"] != curr["patient_id"]:
            continue

        prev_discharge = prev.get("discharge_date")
        curr_admission = curr.get("admission_date")

        if prev_discharge is None or curr_admission is None:
            continue

        days_between = (curr_admission - prev_discharge).days

        if 0 <= days_between <= window_days:
            flags.append(
                {
                    "patient_id": curr["patient_id"],
                    "original_visit_id": prev["visit_id"],
                    "readmission_visit_id": curr["visit_id"],
                    "days_between": days_between,
                    "department": curr["department"],
                }
            )

    return flags


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
    if discharge_date is None:
        return 0.0

    if discharge_date < admission_date:
        return 0.0

    return float((discharge_date - admission_date).days)


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
    return _load_raw_data(context, postgres, "patients")


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
    return _load_raw_data(context, postgres, "visits")


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
    return _load_raw_data(context, postgres, "diagnoses")


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
    return _load_raw_data(context, postgres, "prescriptions")


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
    visits = postgres.execute_query(
        """
        SELECT visit_id, patient_id, department, admission_date, discharge_date
        FROM visits
        WHERE status = 'completed'
        ORDER BY patient_id, admission_date
        """
    )

    visit_dicts = [
        {
            "visit_id": row[0],
            "patient_id": row[1],
            "department": row[2],
            "admission_date": row[3],
            "discharge_date": row[4],
        }
        for row in visits
    ]

    flags = detect_readmissions(visit_dicts, window_days=30)

    flag_count = 0
    if flags:
        flag_count = postgres.load_rows(flags, "readmission_flags")

    context.log.info(f"Loaded {flag_count} readmission flags")

    return dg.MaterializeResult(metadata={"flag_count": flag_count})


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
    context.log.info("📊 Generating patient summary analytics...")

    patients = postgres.execute_query("SELECT patient_id FROM patients")
    context.log.info(f"👥 Processing {len(patients)} patients")

    visits = postgres.execute_query(
        "SELECT patient_id, department, admission_date, discharge_date "
        "FROM visits WHERE status = 'completed'"
    )
    context.log.info(f"📋 Retrieved {len(visits)} visit records")

    prescriptions = postgres.execute_query(
        "SELECT patient_id, end_date FROM prescriptions"
    )
    context.log.info(f"💊 Retrieved {len(prescriptions)} prescription records")

    readmissions = postgres.execute_query("SELECT patient_id FROM readmission_flags")

    readmission_patients = {row[0] for row in readmissions}
    if readmission_patients:
        context.log.info(
            f"⚠️  {len(readmission_patients)} patients have readmission flags"
        )

    patient_visits = defaultdict(list)
    for visit in visits:
        patient_id = visit[0]
        patient_visits[patient_id].append(
            {
                "department": visit[1],
                "admission_date": visit[2],
                "discharge_date": visit[3],
            }
        )

    summaries = []
    risk_distribution = defaultdict(int)

    for patient_row in patients:
        patient_id = patient_row[0]
        visits_list = patient_visits.get(patient_id, [])

        total_visits = len(visits_list)

        if visits_list:
            last_visit = max(v["admission_date"] for v in visits_list)
            last_visit_date = last_visit
        else:
            last_visit_date = None

        if visits_list:
            dept_counts = defaultdict(int)
            for v in visits_list:
                dept_counts[v["department"]] += 1
            primary_department = max(dept_counts, key=dept_counts.get)
        else:
            primary_department = None

        stay_days = []
        for v in visits_list:
            stay = calculate_avg_stay(v["admission_date"], v["discharge_date"])
            stay_days.append(stay)
        avg_stay = sum(stay_days) / len(stay_days) if stay_days else 0.0

        active_count = 0
        for presc in prescriptions:
            if presc[0] == patient_id:
                end_date = presc[1]
                if end_date is None or end_date > datetime.now().date():
                    active_count += 1

        if total_visits >= 5 or patient_id in readmission_patients:
            risk_category = "high"
        elif total_visits >= 3:
            risk_category = "medium"
        else:
            risk_category = "low"

        risk_distribution[risk_category] += 1

        summaries.append(
            {
                "patient_id": patient_id,
                "total_visits": total_visits,
                "last_visit_date": last_visit_date,
                "primary_department": primary_department,
                "avg_stay_days": round(avg_stay, 2),
                "active_prescriptions": active_count,
                "risk_category": risk_category,
            }
        )

    if summaries:
        count = postgres.load_rows(summaries, "patient_summaries")
        context.log.info(f"✅ Created {count} patient summaries")

        context.log.info("📊 Patient Risk Distribution:")
        context.log.info(f"   └─ High risk: {risk_distribution['high']} patients")
        context.log.info(f"   └─ Medium risk: {risk_distribution['medium']} patients")
        context.log.info(f"   └─ Low risk: {risk_distribution['low']} patients")

        avg_visits = sum(s["total_visits"] for s in summaries) / len(summaries)
        avg_active_rx = sum(s["active_prescriptions"] for s in summaries) / len(
            summaries
        )
        context.log.info("📈 Average Metrics:")
        context.log.info(f"   └─ Visits per patient: {avg_visits:.1f}")
        context.log.info(f"   └─ Active prescriptions per patient: {avg_active_rx:.1f}")
    else:
        count = 0
        context.log.warning("⚠️  No patient summaries generated")

    return dg.MaterializeResult(metadata={"patient_count": count})


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
    context.log.info("🏥 Calculating department performance metrics...")

    visits_data = postgres.execute_query(
        "SELECT department, diagnosis_code, admission_date, discharge_date "
        "FROM visits WHERE status = 'completed'"
    )
    context.log.info(f"📊 Retrieved {len(visits_data)} visits for analysis")

    readmissions_data = postgres.execute_query(
        "SELECT department FROM readmission_flags"
    )
    context.log.info(f"🏥 Retrieved {len(readmissions_data)} readmission records")

    dept_stats = defaultdict(
        lambda: {
            "admissions": 0,
            "stay_days": [],
            "diagnoses": defaultdict(int),
            "readmissions": 0,
        }
    )

    for visit in visits_data:
        department = visit[0]
        diagnosis = visit[1]
        admission = visit[2]
        discharge = visit[3]

        dept_stats[department]["admissions"] += 1

        if admission and discharge:
            stay = calculate_avg_stay(admission, discharge)
            dept_stats[department]["stay_days"].append(stay)

        if diagnosis:
            dept_stats[department]["diagnoses"][diagnosis] += 1

    for flag in readmissions_data:
        department = flag[0]
        dept_stats[department]["readmissions"] += 1

    metrics = []
    reporting_period = datetime.now().strftime("%Y-%m")

    context.log.info(f"📊 Computing KPIs for {len(dept_stats)} departments...")

    for department, stats in dept_stats.items():
        total_admissions = stats["admissions"]
        readmission_count = stats["readmissions"]

        if stats["stay_days"]:
            avg_stay = sum(stats["stay_days"]) / len(stats["stay_days"])
        else:
            avg_stay = 0.0

        if total_admissions > 0:
            readmission_rate = readmission_count / total_admissions
        else:
            readmission_rate = 0.0

        if stats["diagnoses"]:
            top_diagnosis = max(stats["diagnoses"], key=stats["diagnoses"].get)
        else:
            top_diagnosis = None

        metrics.append(
            {
                "department": department,
                "reporting_period": reporting_period,
                "total_admissions": total_admissions,
                "avg_stay_days": round(avg_stay, 2),
                "readmission_count": readmission_count,
                "readmission_rate": round(readmission_rate, 4),
                "top_diagnosis_code": top_diagnosis,
                "bed_utilization_rate": 0.75,
            }
        )

    if metrics:
        count = postgres.load_rows(metrics, "department_metrics")
        context.log.info(f"✅ Created metrics for {count} departments")

        context.log.info(
            f"📊 Department Performance Summary (Period: {reporting_period}):"
        )
        for metric in sorted(
            metrics, key=lambda x: x["readmission_rate"], reverse=True
        )[:5]:
            context.log.info(f"   └─ {metric['department']}:")
            context.log.info(f"      ├─ Admissions: {metric['total_admissions']}")
            context.log.info(f"      ├─ Avg Stay: {metric['avg_stay_days']} days")
            context.log.info(
                f"      ├─ Readmission Rate: {metric['readmission_rate'] * 100:.1f}%"
            )
            context.log.info(
                f"      └─ Top Diagnosis: {metric['top_diagnosis_code'] or 'N/A'}"
            )
    else:
        count = 0
        context.log.warning("⚠️  No department metrics generated")

    return dg.MaterializeResult(metadata={"department_count": count})
