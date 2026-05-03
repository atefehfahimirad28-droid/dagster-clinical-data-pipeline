# Klinische Analyse-Pipeline (Dagster)

## Überblick

Produktionsähnliche Datenpipeline mit Dagster zur Verarbeitung **synthetischer klinischer Daten** und Erstellung wöchentlicher Analysen.

Die Pipeline liest CSV-Exporte (Patienten, Besuche, Diagnosen, Rezepte), transformiert sie in analytische Datensätze und lädt die Ergebnisse in PostgreSQL für Reporting und Dashboards.

> Alle Daten sind synthetisch (fiktiv). Es werden keine echten Patientendaten (PHI) verwendet.

---

## Ziel des Projekts

* Orchestrierung von Datenpipelines mit Dagster (Asset-basiert)
* End-to-End Pipeline (Ingestion → Transformation → Laden)
* Aufbau analytischer Datenmodelle
* Grundlagen von CI/CD (Linting, Formatting, Commit-Standards)
* Teamarbeit mit Git

---

## Architektur

**Ingestion (Rohdaten-Assets)**

* `raw_patients`
* `raw_visits`
* `raw_diagnoses`
* `raw_prescriptions`

**Transformationen**

* `patient_summaries`
* `readmission_flags`
* `department_metrics`

**Datenfluss**

```id="m9c7st"
CSV → Dagster Assets → PostgreSQL
```

Zeitplan:

* Wöchentlicher Job (Montag, 07:00 Uhr)

---

## Technologien

* Python
* Dagster
* PostgreSQL
* Docker
* Pytest
* Ruff (Linting & Formatting)

---

## Mein Beitrag

Dies war ein **Gruppenprojekt**. Meine Beiträge:

* Arbeit mit Dagster-Assets und Abhängigkeitsgraph
* Unterstützung bei der Implementierung der Transformationen
* Debugging der Pipeline und Tests
* Behebung von CI-Problemen (Ruff, GitHub Actions)
* Zusammenarbeit im Team mit Git (Commits, Merges, Workflow)

---

## Ausführung

```bash id="o4r0ds"
docker compose up -d
cd clinicflow
uv sync
uv run pytest tests/ -v
dg dev
```

Dagster UI:
http://localhost:3000

---

## Ergebnisse

* Patientenzusammenfassungen
* Abteilungskennzahlen
* Wiederaufnahme-Risikoindikatoren

---

## Kontext

Entwickelt im Rahmen einer Data-Engineering-Weiterbildung mit Fokus auf reale Pipeline-Architektur und Orchestrierung.

---

## Hinweis

Die Referenz auf Charité – Universitätsmedizin Berlin dient ausschließlich als Lernkontext.
Es werden keine echten Systeme oder Daten verwendet.
