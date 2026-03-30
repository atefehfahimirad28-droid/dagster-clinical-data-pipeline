# User Stories -- Klinische Analyse-Pipeline (ClinicFlow)

**Projekt:** Capstone Medical -- Klinische Analyse-Pipeline
**Auftraggeber:** Charite -- Universitaetsmedizin Berlin (Bildungskontext)
**Team:** Junior Data Engineers (Gruppenprojekt)
**Technologien:** Dagster, PostgreSQL, Docker, Python, pandas, psycopg2

> **Hinweis zum Datenschutz:** Alle Patientendaten in diesem Projekt sind vollstaendig synthetisch und fiktiv. Es werden zu keinem Zeitpunkt echte geschuetzte Gesundheitsinformationen (PHI) verwendet. Der Bezug zur Charite dient ausschliesslich dem Bildungskontext.

---

## Agile Arbeitsweise -- Erwartungen

Dieses Projekt folgt einer agilen Arbeitsweise. Jedes Team wird erwartet:

- **Sprint Planning (Tag 1 jedes Sprints):** Backlog pruefen, User Stories fuer den Sprint auswaehlen, Verantwortlichkeiten zuweisen, Stories bei Bedarf in Aufgaben zerlegen.
- **Daily Standup (max. 15 Min.):** Jedes Teammitglied beantwortet: Was habe ich gestern gemacht? Was mache ich heute? Gibt es Blocker?
- **Sprint Review (letzter Tag des Sprints):** Fertige Arbeit dem Dozenten/den Stakeholdern demonstrieren. Funktionierende Software zeigen (Dagit-UI, gruene Tests, CI-Pipeline).
- **Sprint Retrospektive (nach dem Review):** Besprechen, was gut lief, was verbessert werden kann, und eine konkrete Massnahme fuer den naechsten Sprint vereinbaren.

Nutzt ein Projektboard (GitHub Projects, Trello o.Ae.) zur Nachverfolgung des Story-Status: **To Do**, **In Arbeit**, **Im Review**, **Fertig**.

---

## Vorgeschlagener Sprint-Plan

| Sprint   | Dauer    | Epics                                | Schwerpunkt                                   |
|----------|----------|--------------------------------------|-----------------------------------------------|
| Sprint 1 | ~3 Tage  | Epic 1 (Projektsetup & CI/CD) + Epic 2 (Infrastruktur & Ressourcen) | Fundament: Repository, CI/CD, Docker, PostgresResource |
| Sprint 2 | ~4 Tage  | Epic 3 (Datenaufnahme) + Epic 4 (Klinische Transformationen)        | Kern-Pipeline: Roh-Assets + Analysen          |
| Sprint 3 | ~3 Tage  | Epic 5 (Orchestrierung) + Epic 6 (Dokumentation & Demo)             | Scheduling, End-to-End-Test, Demo-Vorbereitung|

---

## Definition of Done

Eine User Story gilt als **Fertig**, wenn alle folgenden Kriterien erfuellt sind:

- [ ] Alle Akzeptanzkriterien sind erfuellt
- [ ] Alle relevanten Unit-/Integrationstests bestehen (`uv run pytest tests/ -v`)
- [ ] Der Code wurde von mindestens einem anderen Teammitglied reviewed (PR genehmigt)
- [ ] Die CI-Pipeline ist gruen (Linting + Tests bestehen im PR)
- [ ] Der Code ist in den `main`-Branch gemergt
- [ ] Neue Funktionalitaet ist dokumentiert (Docstrings, Kommentare wo noetig)

---

## Branching-Strategie

```
main                          (geschuetzt -- Merge nur via PR)
  ├── feature/US-01-repo-setup
  ├── feature/US-02-ci-pipeline
  ├── feature/US-07-raw-patients
  └── ...
```

- **`main`**: Immer stabil und deploybar. Geschuetzt -- keine direkten Pushes.
- **`feature/US-XX-kurzbeschreibung`**: Ein Branch pro User Story. Wird von `main` erstellt und per Pull Request zurueck in `main` gemergt.

Regeln:
1. Niemals direkt auf `main` pushen.
2. Jeder Merge erfordert einen Pull Request mit bestandener CI.
3. Feature-Branches nach dem Mergen loeschen.

---

## Datenschutz-Hinweise

- Alle Datendateien (`data/*.csv`) enthalten **synthetische, computergenerierte Datensaetze**. Es werden zu keinem Zeitpunkt echte Patientendaten verwendet.
- Auch mit synthetischen Daten: Behandelt das Projekt so, als waeren es echte Daten. Keine Zugangsdaten committen, keine Datenbank-Ports oeffentlich freigeben, `.env`-Dateien fuer Secrets verwenden und in `.gitignore` eintragen.
- In den Architecture Decision Records (US-16) soll diskutiert werden, welche Datenschutzmassnahmen fuer eine echte klinische Daten-Pipeline erforderlich waeren (z.B. DSGVO, HIPAA, Anonymisierung, Zugriffskontrolle, Audit-Logging).

---

## Epic 1: Projektsetup & CI/CD

### US-01: Repository und Branching-Strategie einrichten

**Als** Entwicklungsteam
**moechte ich** ein korrekt konfiguriertes Git-Repository mit einer Branching-Strategie,
**damit** wir ohne Merge-Konflikte zusammenarbeiten und die Codequalitaet sicherstellen koennen.

**Akzeptanzkriterien:**
- [ ] GitHub-Repository ist erstellt und alle Teammitglieder haben Push-Zugriff
- [ ] `main`-Branch existiert und ist geschuetzt (kein direktes Pushen, PR-Review erforderlich)
- [ ] Branch-Namenskonvention `feature/US-XX-beschreibung` ist dokumentiert und vereinbart
- [ ] `.gitignore` enthaelt `.venv/`, `__pycache__/`, `.env`, `.dagster/`, `*.pyc`
- [ ] Alle Teammitglieder haben das Repository geklont und koennen Feature-Branches erstellen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Team Lead / DevOps

---

### US-02: CI-Pipeline mit GitHub Actions

**Als** Entwicklungsteam
**moechte ich** eine automatisierte CI-Pipeline, die jeden Pull Request lintet und testet,
**damit** wir Fehler frueh erkennen und die Codequalitaet aufrechterhalten.

**Akzeptanzkriterien:**
- [ ] `.github/workflows/ci.yml` existiert und wird bei jedem PR auf `main` ausgefuehrt
- [ ] Pipeline installiert Abhaengigkeiten mit `uv sync --dev`
- [ ] Pipeline fuehrt `ruff check .` fuer Linting aus (keine Verstoesse erlaubt)
- [ ] Pipeline fuehrt `uv run pytest tests/ -v` aus und schlaegt fehl, wenn ein Test fehlschlaegt
- [ ] PR-Merge wird blockiert, wenn die CI-Pipeline fehlschlaegt (Branch-Schutzregel)
- [ ] Pipeline laeuft auf Python 3.10+ (entsprechend der Projektanforderung)

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** DevOps / CI-Engineer

---

### US-03: CD-Pipeline fuer Deployment-Bereitschaft

**Als** Entwicklungsteam
**moechte ich** eine CD-Pipeline, die Docker-Builds und Infrastruktur-Health-Checks verifiziert,
**damit** wir wissen, dass unsere Anwendung jederzeit deploybar ist.

**Akzeptanzkriterien:**
- [ ] CI/CD-Workflow enthaelt einen Schritt, der `docker compose build` ausfuehrt und den Erfolg verifiziert
- [ ] Ein Schritt fuehrt `docker compose up -d` aus und verifiziert, dass alle Services einen gesunden Zustand erreichen
- [ ] PostgreSQL-Health-Check besteht (Verbindungstest mit `pg_isready` o.Ae.)
- [ ] Pipeline raeumt Docker-Ressourcen nach der Verifikation auf (`docker compose down`)
- [ ] Pipeline laeuft auf dem `main`-Branch nach dem Merge (oder nach Zeitplan)

**Story Points:** 3 (mittel)
**Prioritaet:** Should Have
**Vorgeschlagene Zuweisung:** DevOps / CI-Engineer

---

### US-04: Entwicklungsumgebung einrichten

**Als** Teammitglied
**moechte ich** eine funktionierende lokale Entwicklungsumgebung,
**damit** ich Pipeline-Code auf meinem Rechner entwickeln und testen kann.

**Akzeptanzkriterien:**
- [ ] `docker compose up -d` startet PostgreSQL mit der `clinicflow`-Datenbank und dem Schema
- [ ] `uv sync --dev` installiert alle Python-Abhaengigkeiten ohne Fehler
- [ ] `uv run pytest tests/ -v` laeuft (Tests duerfen fehlschlagen, aber der Test-Runner funktioniert)
- [ ] `dg dev` startet den Dagster-Dev-Server und die Dagit-UI ist unter `localhost:3000` erreichbar
- [ ] Jedes Teammitglied hat bestaetigt, dass seine Umgebung funktioniert (in einer Checkliste dokumentiert)
- [ ] Eine kurze `SETUP.md` oder ein Abschnitt in der README beschreibt die Einrichtungsschritte

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Alle Teammitglieder

---

## Epic 2: Infrastruktur & Ressourcen

### US-05: PostgreSQL-Datenbank einrichten

**Als** Data Engineer
**moechte ich** eine PostgreSQL-Datenbank in Docker mit vordefinierten Tabellen,
**damit** unsere Pipeline ein Ziel hat, in das Daten geladen werden koennen.

**Akzeptanzkriterien:**
- [ ] `docker compose up -d` startet PostgreSQL 17 auf Port 5432
- [ ] Die `clinicflow`-Datenbank wird automatisch erstellt
- [ ] `init.sql` erstellt alle benoetigten Tabellen: `patients`, `visits`, `diagnoses`, `prescriptions`, `readmission_flags`, `patient_summaries`, `department_metrics`
- [ ] Tabellen entsprechen dem erwarteten Schema der Assets (korrekte Spaltennamen und -typen)
- [ ] Die Datenbank ist mit den Zugangsdaten aus `docker-compose.yml` erreichbar
- [ ] `docker compose down -v` gefolgt von `docker compose up -d` liefert eine saubere Datenbank

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Infrastruktur / Backend

---

### US-06: PostgresResource implementieren

**Als** Data Engineer
**moechte ich** eine wiederverwendbare Dagster-Ressource fuer PostgreSQL-Operationen,
**damit** alle Assets ueber eine einheitliche Schnittstelle mit der Datenbank interagieren koennen.

**Akzeptanzkriterien:**
- [ ] `PostgresResource`-Klasse ist in `src/clinicflow/defs/resources.py` implementiert
- [ ] `get_connection()` gibt eine gueltige `psycopg2`-Verbindung zur clinicflow-Datenbank zurueck
- [ ] `execute_query(query, params)` fuehrt eine SQL-Anweisung aus und gibt Ergebnisse fuer SELECT-Abfragen zurueck
- [ ] `load_dataframe(df, table_name)` fuegt einen pandas DataFrame per Bulk-Insert in die angegebene Tabelle ein und gibt die Zeilenanzahl zurueck
- [ ] Verbindungen werden nach der Nutzung ordnungsgemaess geschlossen (Context Manager oder explizites Schliessen)
- [ ] Unit-Tests fuer die Ressourcen-Methoden bestehen

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Backend-Entwickler

---

## Epic 3: Datenaufnahme (Roh-Assets)

### US-07: raw_patients-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `patients.csv` in PostgreSQL laedt,
**damit** Patientendaten fuer nachgelagerte Analysen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_patients`-Asset liest `data/patients.csv` mit pandas
- [ ] Daten werden ueber `postgres.load_dataframe()` in die `patients`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Patienten
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A

---

### US-08: raw_visits-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `visits.csv` in PostgreSQL laedt,
**damit** Besuchsdaten fuer Wiederaufnahme-Erkennung und Abteilungsmetriken verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_visits`-Asset liest `data/visits.csv` mit pandas
- [ ] Daten werden ueber `postgres.load_dataframe()` in die `visits`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Besuche
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer B

---

### US-09: raw_diagnoses-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `diagnoses.csv` in PostgreSQL laedt,
**damit** Diagnosedaten fuer Abteilungsmetriken und Analysen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_diagnoses`-Asset liest `data/diagnoses.csv` mit pandas
- [ ] Daten werden ueber `postgres.load_dataframe()` in die `diagnoses`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Diagnosen
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A

---

### US-10: raw_prescriptions-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `prescriptions.csv` in PostgreSQL laedt,
**damit** Verschreibungsdaten fuer Patientenzusammenfassungen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_prescriptions`-Asset liest `data/prescriptions.csv` mit pandas
- [ ] Daten werden ueber `postgres.load_dataframe()` in die `prescriptions`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Verschreibungen
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer B

---

## Epic 4: Klinische Transformationen

### US-11: patient_summaries-Asset implementieren

**Als** klinischer Datenanalyst
**moechte ich** aggregierte Statistiken pro Patient aus mehreren Datenquellen,
**damit** Kliniker schnell das klinische Profil und die Risikostufe jedes Patienten einschaetzen koennen.

**Akzeptanzkriterien:**
- [ ] Asset haengt von `raw_patients`, `raw_visits` und `raw_prescriptions` ab
- [ ] Berechnet pro Patient: `total_visits`, `avg_stay_days`, `last_visit_date`, `primary_department`, Anzahl `active_prescriptions`
- [ ] Weist `risk_category` zu: "high" wenn total_visits >= 5 oder Patient eine Wiederaufnahme hat, "medium" wenn total_visits >= 3, "low" sonst
- [ ] Ergebnisse werden in die Tabelle `patient_summaries` eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `patient_count`-Metadaten zurueck
- [ ] Die Hilfsfunktion `calculate_avg_stay()` ist implementiert und getestet
- [ ] Asset gehoert zur Gruppe `analytics`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 5 (gross)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A + B (Pair Programming empfohlen)

---

### US-12: readmission_flags-Asset implementieren

**Als** Qualitaetsmanagement-Beauftragter
**moechte ich**, dass Patienten, die innerhalb eines konfigurierbaren Zeitfensters (Standard: 30 Tage) wiederaufgenommen werden, gekennzeichnet werden,
**damit** das Krankenhaus potenziell vermeidbare Wiederaufnahmen identifizieren und untersuchen kann.

**Akzeptanzkriterien:**
- [ ] Asset haengt von `raw_visits` ab
- [ ] Fragt alle abgeschlossenen Besuche ab, sortiert nach `patient_id` und `admission_date`
- [ ] Verwendet die Hilfsfunktion `detect_readmissions()` zur Erkennung von Wiederaufnahmen innerhalb des konfigurierten Zeitfensters
- [ ] `detect_readmissions()` gibt Dicts mit folgenden Schluesseln zurueck: `patient_id`, `original_visit_id`, `readmission_visit_id`, `days_between`, `department`
- [ ] Wiederaufnahme-Flags werden in die Tabelle `readmission_flags` eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `flag_count`-Metadaten zurueck
- [ ] Das Wiederaufnahme-Zeitfenster ist konfigurierbar (Standard: 30 Tage)
- [ ] Asset gehoert zur Gruppe `analytics`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 5 (gross)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer B

---

### US-13: department_metrics-Asset implementieren

**Als** Abteilungsleiter
**moechte ich** pro Abteilung berechnete Leistungskennzahlen (KPIs) aus Besuchs- und Diagnosedaten,
**damit** ich die klinische Leistung meiner Abteilung bewerten und Verbesserungspotenziale identifizieren kann.

**Akzeptanzkriterien:**
- [ ] Asset haengt von `raw_visits`, `raw_diagnoses` und `readmission_flags` ab
- [ ] Berechnet pro Abteilung: `total_admissions`, `avg_stay_days`, `readmission_count`, `readmission_rate`, `top_diagnosis_code`
- [ ] `readmission_rate` wird berechnet als `readmission_count / total_admissions`
- [ ] `bed_utilization_rate` wird auf einen Platzhalterwert (0,75) gesetzt oder bei Bedarf berechnet
- [ ] `reporting_period` wird auf aktuelles Jahr-Monat oder "all-time" gesetzt
- [ ] Ergebnisse werden in die Tabelle `department_metrics` eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `department_count`-Metadaten zurueck
- [ ] Asset gehoert zur Gruppe `analytics`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 5 (gross)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A

---

## Epic 5: Orchestrierung

### US-14: weekly_analytics_schedule implementieren

**Als** Datenplattform-Betreiber
**moechte ich**, dass die Analyse-Pipeline automatisch jeden Montag um 07:00 Uhr laeuft,
**damit** klinische Berichte woechentlich ohne manuellen Eingriff aktualisiert werden.

**Akzeptanzkriterien:**
- [ ] `weekly_analytics_job` ist in `src/clinicflow/defs/jobs.py` definiert und waehlt alle Assets aus
- [ ] `readmission_screening_job` ist definiert und waehlt nur Wiederaufnahme- und Patientenzusammenfassungs-Assets aus
- [ ] `weekly_analytics_schedule` ist in `src/clinicflow/defs/schedules.py` definiert
- [ ] Schedule loest `weekly_analytics_job` mit einem Cron-Ausdruck fuer jeden Montag um 07:00 aus (`0 7 * * 1`)
- [ ] Schedule ist in der Dagit-UI sichtbar und registriert
- [ ] Zugehoerige Tests bestehen

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A oder B

---

### US-15: End-to-End-Pipeline-Test in Dagit

**Als** Team
**moechte ich** verifizieren, dass die gesamte Pipeline end-to-end in Dagit funktioniert,
**damit** wir ein funktionierendes System selbstbewusst demonstrieren und abliefern koennen.

**Akzeptanzkriterien:**
- [ ] Alle Assets koennen in der Dagit-UI nacheinander ohne Fehler materialisiert werden
- [ ] Der Asset-Graph in Dagit zeigt die korrekte Abhaengigkeitsstruktur gemaess dem Architekturdiagramm
- [ ] Die Tabelle `patient_summaries` enthaelt nach der Materialisierung aggregierte Daten
- [ ] Die Tabelle `readmission_flags` enthaelt nach der Materialisierung gekennzeichnete Wiederaufnahmen
- [ ] Die Tabelle `department_metrics` enthaelt nach der Materialisierung KPIs pro Abteilung
- [ ] Alle 12 Tests bestehen (`uv run pytest tests/ -v`)
- [ ] Keine unbehandelten Fehler oder Warnungen in den Dagster-Logs

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Gesamtes Team

---

## Epic 6: Dokumentation & Demo

### US-16: Architecture Decision Records schreiben

**Als** Team
**moechte ich** dokumentierte Architekturentscheidungen,
**damit** zukuenftige Entwickler verstehen, warum wir bestimmte Technologien und Ansaetze gewaehlt haben.

**Akzeptanzkriterien:**
- [ ] ADR-Dokument existiert (z.B. `docs/adr/` oder ein Abschnitt in der README)
- [ ] ADR-001: Warum Dagster als Orchestrator gewaehlt wurde (vs. Airflow, Prefect etc.)
- [ ] ADR-002: Datenschutzueberlegungen fuer klinische Daten (DSGVO, Anonymisierung, Zugriffskontrolle, Audit-Logging -- auch wenn die Daten synthetisch sind, soll diskutiert werden, was fuer echte PHI erforderlich waere)
- [ ] ADR-003: Entscheidungen zum Datenbankschema-Design (Warum diese Tabellen, Normalisierungsentscheidungen)
- [ ] Jeder ADR folgt einem einheitlichen Format: Kontext, Entscheidung, Konsequenzen
- [ ] ADRs sind vom Team reviewed

**Story Points:** 3 (mittel)
**Prioritaet:** Should Have
**Vorgeschlagene Zuweisung:** Dokumentations-Verantwortlicher / Alle Teammitglieder

---

### US-17: Live-Demo in Dagit vorbereiten

**Als** Team
**moechte ich** eine ausgefeilte Live-Demo der Pipeline in Dagit,
**damit** wir unsere Arbeit Dozenten und Stakeholdern praesentieren koennen.

**Akzeptanzkriterien:**
- [ ] Demo-Skript ist vorbereitet und umfasst: Asset-Graph-Uebersicht, Materialisierungslauf, Schedule-Konfiguration
- [ ] Asset-Graph wird in Dagit mit allen Gruppen und Abhaengigkeiten uebersichtlich angezeigt
- [ ] Wiederaufnahme-Erkennung wird demonstriert: `readmission_flags` materialisieren, Ergebnisse abfragen, Logik erklaeren
- [ ] Abteilungsmetriken-Daten werden gezeigt: `department_metrics` materialisieren, Ergebnisse aus PostgreSQL abfragen
- [ ] Schedule `weekly_analytics_schedule` wird als registriert und aktiv angezeigt
- [ ] Das Team kann Fragen zu Architekturentscheidungen, Fehlerbehandlung und Konfiguration beantworten
- [ ] Demo laeuft ohne Fehler (mindestens einmal geprobt)

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Gesamtes Team (einen Demo-Verantwortlichen benennen)

---

## Uebersichtstabelle

| ID    | Titel                                    | Punkte | Prioritaet    | Epic |
|-------|------------------------------------------|--------|---------------|------|
| US-01 | Repository und Branching-Strategie       | 2      | Must Have     | 1    |
| US-02 | CI-Pipeline mit GitHub Actions           | 3      | Must Have     | 1    |
| US-03 | CD-Pipeline fuer Deployment              | 3      | Should Have   | 1    |
| US-04 | Entwicklungsumgebung einrichten          | 2      | Must Have     | 1    |
| US-05 | PostgreSQL-Datenbank einrichten          | 2      | Must Have     | 2    |
| US-06 | PostgresResource implementieren          | 3      | Must Have     | 2    |
| US-07 | raw_patients-Asset implementieren        | 2      | Must Have     | 3    |
| US-08 | raw_visits-Asset implementieren          | 2      | Must Have     | 3    |
| US-09 | raw_diagnoses-Asset implementieren       | 2      | Must Have     | 3    |
| US-10 | raw_prescriptions-Asset implementieren   | 2      | Must Have     | 3    |
| US-11 | patient_summaries-Asset implementieren   | 5      | Must Have     | 4    |
| US-12 | readmission_flags-Asset implementieren   | 5      | Must Have     | 4    |
| US-13 | department_metrics-Asset implementieren  | 5      | Must Have     | 4    |
| US-14 | weekly_analytics_schedule                | 3      | Must Have     | 5    |
| US-15 | End-to-End-Pipeline-Test                 | 3      | Must Have     | 5    |
| US-16 | Architecture Decision Records            | 3      | Should Have   | 6    |
| US-17 | Live-Demo in Dagit vorbereiten           | 3      | Must Have     | 6    |
| **Gesamt** |                                     | **50** |               |      |
