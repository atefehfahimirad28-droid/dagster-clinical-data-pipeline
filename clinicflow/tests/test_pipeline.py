"""TDD tests for the Charite Clinical Analytics Pipeline.

These tests verify the pipeline structure, asset dependencies, job
definitions, and pure calculation logic WITHOUT requiring a running
PostgreSQL database.

Run with: uv run pytest tests/ -v

German: TDD-Tests fuer die klinische Analyse-Pipeline der Charite.

Diese Tests ueberpruefen die Pipeline-Struktur, Asset-Abhaengigkeiten,
Job-Definitionen und reine Berechnungslogik OHNE eine laufende
PostgreSQL-Datenbank.
"""

from datetime import date, datetime

import dagster as dg

from clinicflow.defs.assets import (
    calculate_avg_stay,
    department_metrics,
    detect_readmissions,
    patient_summaries,
    raw_diagnoses,
    raw_patients,
    raw_prescriptions,
    raw_visits,
    readmission_flags,
)
from clinicflow.defs.jobs import (
    readmission_screening_job,
    weekly_analytics_job,
)
from clinicflow.defs.resources import PostgresResource

# ---------------------------------------------------------------------------
# Helper: build a minimal Definitions object for graph introspection
# DE: Hilfsfunktion: ein minimales Definitions-Objekt fuer Graph-Inspektion erstellen
# ---------------------------------------------------------------------------


def _get_all_assets():
    """Return all asset definitions as a list.

    DE: Gibt alle Asset-Definitionen als Liste zurueck.
    """
    return [
        raw_patients,
        raw_visits,
        raw_diagnoses,
        raw_prescriptions,
        readmission_flags,
        patient_summaries,
        department_metrics,
    ]


def _get_asset_by_key(key_name: str):
    """Return the AssetsDefinition for a given asset key name.

    DE: Gibt die AssetsDefinition fuer einen bestimmten Asset-Schluessel zurueck.
    """
    for asset_def in _get_all_assets():
        if dg.AssetKey(key_name) in asset_def.keys:
            return asset_def
    raise ValueError(f"No asset with key {key_name}")


# ---------------------------------------------------------------------------
# Test 1: PostgresResource configuration
# DE: Test 1: PostgresResource-Konfiguration
# ---------------------------------------------------------------------------


class TestPostgresResourceConfig:
    """Verify that PostgresResource can be instantiated with a connection string.

    DE: Ueberprueft, dass PostgresResource mit einem Verbindungsstring
    instanziiert werden kann.
    """

    def test_postgres_resource_config(self):
        resource = PostgresResource(
            connection_string="postgresql://test:test@localhost:5432/testdb"
        )
        assert (
            resource.connection_string == "postgresql://test:test@localhost:5432/testdb"
        )

    def test_postgres_resource_default_config(self):
        resource = PostgresResource()
        assert "clinicflow" in resource.connection_string


# ---------------------------------------------------------------------------
# Tests 2-5: Raw asset existence
# DE: Tests 2-5: Existenz der Rohdaten-Assets
# ---------------------------------------------------------------------------


class TestRawAssetExistence:
    """Verify that all four raw ingestion assets are defined.

    DE: Ueberprueft, dass alle vier Rohdaten-Aufnahme-Assets definiert sind.
    """

    def test_raw_patients_asset_exists(self):
        keys = {asset.key for asset in _get_all_assets()}
        assert dg.AssetKey("raw_patients") in keys

    def test_raw_visits_asset_exists(self):
        keys = {asset.key for asset in _get_all_assets()}
        assert dg.AssetKey("raw_visits") in keys

    def test_raw_diagnoses_asset_exists(self):
        keys = {asset.key for asset in _get_all_assets()}
        assert dg.AssetKey("raw_diagnoses") in keys

    def test_raw_prescriptions_asset_exists(self):
        keys = {asset.key for asset in _get_all_assets()}
        assert dg.AssetKey("raw_prescriptions") in keys


# ---------------------------------------------------------------------------
# Tests 6-8: Asset dependency structure
# DE: Tests 6-8: Asset-Abhaengigkeitsstruktur
# ---------------------------------------------------------------------------


class TestAssetDependencies:
    """Verify the asset dependency graph is wired correctly.

    DE: Ueberprueft, dass der Asset-Abhaengigkeitsgraph korrekt verdrahtet ist.
    """

    def test_patient_summaries_depends_on_raw_assets(self):
        """patient_summaries should depend on raw_patients, raw_visits,
        and raw_prescriptions.

        DE: patient_summaries sollte von raw_patients, raw_visits und
        raw_prescriptions abhaengen.
        """
        asset_def = _get_asset_by_key("patient_summaries")
        dep_keys = asset_def.dependency_keys
        expected = {
            dg.AssetKey("raw_patients"),
            dg.AssetKey("raw_visits"),
            dg.AssetKey("raw_prescriptions"),
        }
        assert expected.issubset(dep_keys), (
            f"patient_summaries deps: {dep_keys}, expected at least {expected}"
        )

    def test_department_metrics_depends_on_visits(self):
        """department_metrics should depend on raw_visits, raw_diagnoses,
        and readmission_flags.

        DE: department_metrics sollte von raw_visits, raw_diagnoses und
        readmission_flags abhaengen.
        """
        asset_def = _get_asset_by_key("department_metrics")
        dep_keys = asset_def.dependency_keys
        assert dg.AssetKey("raw_visits") in dep_keys
        assert dg.AssetKey("raw_diagnoses") in dep_keys
        assert dg.AssetKey("readmission_flags") in dep_keys

    def test_readmission_flags_depends_on_raw_visits(self):
        """readmission_flags should depend on raw_visits.

        DE: readmission_flags sollte von raw_visits abhaengen.
        """
        asset_def = _get_asset_by_key("readmission_flags")
        dep_keys = asset_def.dependency_keys
        assert dg.AssetKey("raw_visits") in dep_keys


# ---------------------------------------------------------------------------
# Test 9: Job definition
# DE: Test 9: Job-Definition
# ---------------------------------------------------------------------------


class TestJobDefinitions:
    """Verify that jobs are properly defined.

    DE: Ueberprueft, dass Jobs korrekt definiert sind.
    """

    def test_weekly_analytics_job_defined(self):
        assert weekly_analytics_job.name == "weekly_analytics_job"

    def test_readmission_screening_job_defined(self):
        assert readmission_screening_job.name == "readmission_screening_job"


# ---------------------------------------------------------------------------
# Tests 10-11: Readmission detection logic (pure function)
# DE: Tests 10-11: Wiederaufnahme-Erkennungslogik (reine Funktion)
# ---------------------------------------------------------------------------


class TestReadmissionDetection:
    """Unit tests for the detect_readmissions() pure helper function.

    DE: Unit-Tests fuer die reine Hilfsfunktion detect_readmissions().
    """

    def test_readmission_detection_within_window(self):
        """Visits within 30 days of each other should be flagged.

        DE: Besuche innerhalb von 30 Tagen sollten als Wiederaufnahme markiert werden.
        """
        visits = [
            {
                "visit_id": "V001",
                "patient_id": "P001",
                "department": "Cardiology",
                "admission_date": date(2024, 1, 5),
                "discharge_date": date(2024, 1, 9),
            },
            {
                "visit_id": "V002",
                "patient_id": "P001",
                "department": "Cardiology",
                "admission_date": date(2024, 1, 28),
                "discharge_date": date(2024, 1, 30),
            },
        ]
        flags = detect_readmissions(visits, window_days=30)
        assert len(flags) == 1
        assert flags[0]["patient_id"] == "P001"
        assert flags[0]["original_visit_id"] == "V001"
        assert flags[0]["readmission_visit_id"] == "V002"
        assert flags[0]["days_between"] == 19  # Jan 9 -> Jan 28

    def test_readmission_detection_outside_window(self):
        """Visits more than 30 days apart should NOT be flagged.

        DE: Besuche mit mehr als 30 Tagen Abstand sollten NICHT markiert werden.
        """
        visits = [
            {
                "visit_id": "V001",
                "patient_id": "P001",
                "department": "Cardiology",
                "admission_date": date(2024, 1, 5),
                "discharge_date": date(2024, 1, 9),
            },
            {
                "visit_id": "V002",
                "patient_id": "P001",
                "department": "Cardiology",
                "admission_date": date(2024, 3, 15),
                "discharge_date": date(2024, 3, 18),
            },
        ]
        flags = detect_readmissions(visits, window_days=30)
        assert len(flags) == 0

    def test_readmission_different_patients_not_flagged(self):
        """Visits by different patients should not trigger readmission flags.

        DE: Besuche verschiedener Patienten sollten keine
        Wiederaufnahme-Flags ausloesen.
        """
        visits = [
            {
                "visit_id": "V001",
                "patient_id": "P001",
                "department": "Cardiology",
                "admission_date": date(2024, 1, 5),
                "discharge_date": date(2024, 1, 9),
            },
            {
                "visit_id": "V002",
                "patient_id": "P002",
                "department": "Cardiology",
                "admission_date": date(2024, 1, 10),
                "discharge_date": date(2024, 1, 12),
            },
        ]
        flags = detect_readmissions(visits, window_days=30)
        assert len(flags) == 0


# ---------------------------------------------------------------------------
# Test 12: Average stay calculation (pure function)
# DE: Test 12: Berechnung der durchschnittlichen Aufenthaltsdauer (reine Funktion)
# ---------------------------------------------------------------------------


class TestAvgStayCalculation:
    """Unit test for the calculate_avg_stay() helper.

    DE: Unit-Test fuer die Hilfsfunktion calculate_avg_stay().
    """

    def test_avg_stay_calculation(self):
        """A 4-day stay should return 4.0.

        DE: Ein 4-taegiger Aufenthalt sollte 4.0 zurueckgeben.
        """
        result = calculate_avg_stay(
            datetime(2024, 1, 5),
            datetime(2024, 1, 9),
        )
        assert result == 4.0

    def test_avg_stay_same_day(self):
        """Same-day visit should return 0.0.

        DE: Ein Besuch am selben Tag sollte 0.0 zurueckgeben.
        """
        result = calculate_avg_stay(
            datetime(2024, 1, 5),
            datetime(2024, 1, 5),
        )
        assert result == 0.0
