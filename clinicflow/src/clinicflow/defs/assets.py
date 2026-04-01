import csv
from datetime import datetime
from pathlib import Path

import dagster as dg

from clinicflow.defs.resources import PostgresResource

DATA_DIR = Path(__file__).resolve().parents[4] / "data"


def detect_readmissions(
    visits: list[dict],
    window_days: int = 30,
) -> list[dict]:
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
    if discharge_date is None:
        return 0.0

    if discharge_date < admission_date:
        return 0.0

    return float((discharge_date - admission_date).days)


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_patients(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    with open(
        DATA_DIR / "patients.csv",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    count = postgres.load_rows(rows, "patients")
    context.log.info(f"Loaded {count} patients")

    return dg.MaterializeResult(metadata={"row_count": count})


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_visits(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    with open(
        DATA_DIR / "visits.csv",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    count = postgres.load_rows(rows, "visits")
    context.log.info(f"Loaded {count} visits")

    return dg.MaterializeResult(metadata={"row_count": count})


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_diagnoses(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    with open(
        DATA_DIR / "diagnoses.csv",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    count = postgres.load_rows(rows, "diagnoses")
    context.log.info(f"Loaded {count} diagnoses")

    return dg.MaterializeResult(metadata={"row_count": count})


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "postgres"},
)
def raw_prescriptions(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    with open(
        DATA_DIR / "prescriptions.csv",
        newline="",
        encoding="utf-8",
    ) as f:
        rows = list(csv.DictReader(f))

    count = postgres.load_rows(rows, "prescriptions")
    context.log.info(f"Loaded {count} prescriptions")

    return dg.MaterializeResult(metadata={"row_count": count})


@dg.asset(
    deps=[raw_visits],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def readmission_flags(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
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


@dg.asset(
    deps=[raw_patients, raw_visits, raw_prescriptions],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def patient_summaries(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    raise NotImplementedError("TODO: Implement patient_summaries asset")


@dg.asset(
    deps=[raw_visits, raw_diagnoses, readmission_flags],
    group_name="analytics",
    kinds={"python", "postgres"},
)
def department_metrics(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    raise NotImplementedError("TODO: Implement department_metrics asset")
