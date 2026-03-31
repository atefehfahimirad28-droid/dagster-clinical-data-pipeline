# User Stories -- Klinische Analyse-Pipeline (ClinicFlow)

**Projekt:** Capstone Medical -- Klinische Analyse-Pipeline
**Auftraggeber:** Charite -- Universitaetsmedizin Berlin (Bildungskontext)
**Team:** Junior Data Engineers (Gruppenprojekt)
**Technologien:** Dagster, PostgreSQL, Docker, Python, psycopg2

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

Sprints sind stuendliche Bloecke ueber einen Zeitraum von 2 Tagen. Jeder Sprint umfasst ein kurzes Standup, fokussierte Arbeit und ein kurzes Review.

### Tag 1

| Sprint   | Dauer    | Epics / Stories           | Schwerpunkt                                   |
|----------|----------|---------------------------|-----------------------------------------------|
| Sprint 1 | 1 Stunde | Epic 1: US-01             | `PostgresResource` implementieren (`get_connection`, `execute_query`, `load_rows`) |
| Sprint 2 | 1 Stunde | Epic 2: US-02, US-03      | Rohdaten-Aufnahme: `raw_patients`, `raw_visits` |
| Sprint 3 | 1 Stunde | Epic 2: US-04, US-05      | Rohdaten-Aufnahme: `raw_diagnoses`, `raw_prescriptions` |
| Sprint 4 | 1 Stunde | Epic 3: US-07             | `detect_readmissions()`-Hilfsfunktion + `readmission_flags`-Asset |
| Sprint 5 | 1 Stunde | Epic 3: US-06             | `calculate_avg_stay()`-Hilfsfunktion + `patient_summaries`-Asset |

### Tag 2

| Sprint   | Dauer    | Epics / Stories           | Schwerpunkt                                   |
|----------|----------|---------------------------|-----------------------------------------------|
| Sprint 6 | 1 Stunde | Epic 3: US-08             | `department_metrics`-Asset                    |
| Sprint 7 | 1 Stunde | Epic 4: US-09, US-10      | Jobs, Schedule, End-to-End-Verifikation       |
| Sprint 8 | 1 Stunde | Epic 5: US-11, US-12      | Architecture Decision Records + Demo-Vorbereitung |
| Sprint 9 | 1 Stunde | Epic 6--7: US-13--US-15   | Fortgeschrittene / Erweiterungs-Stories (optional) |

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
  ├── feature/US-01-postgres-resource
  ├── feature/US-02-raw-patients
  ├── feature/US-06-patient-summaries
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
- In den Architecture Decision Records (US-11) soll diskutiert werden, welche Datenschutzmassnahmen fuer eine echte klinische Daten-Pipeline erforderlich waeren (z.B. DSGVO, HIPAA, Anonymisierung, Zugriffskontrolle, Audit-Logging).

---

## Epic 1: Ressourcen

### US-01: PostgresResource implementieren

**Als** Data Engineer
**moechte ich** eine wiederverwendbare Dagster-Ressource fuer PostgreSQL-Operationen,
**damit** alle Assets ueber eine einheitliche Schnittstelle mit der Datenbank interagieren koennen.

**Akzeptanzkriterien:**
- [ ] `PostgresResource`-Klasse ist in `src/clinicflow/defs/resources.py` implementiert
- [ ] `get_connection()` gibt eine gueltige `psycopg2`-Verbindung zur clinicflow-Datenbank zurueck
- [ ] `execute_query(query, params)` fuehrt eine SQL-Anweisung aus und gibt Ergebnisse fuer SELECT-Abfragen zurueck
- [ ] `load_rows(rows, table_name)` fuegt eine Liste von Dicts per Bulk-Insert in die angegebene Tabelle ein und gibt die Zeilenanzahl zurueck
- [ ] Verbindungen werden nach der Nutzung ordnungsgemaess geschlossen (Context Manager oder explizites Schliessen)
- [ ] Unit-Tests fuer die Ressourcen-Methoden bestehen

**Story Points:** 3 (mittel)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Backend-Entwickler

---

## Epic 2: Datenaufnahme (Roh-Assets)

### US-02: raw_patients-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `patients.csv` in PostgreSQL laedt,
**damit** Patientendaten fuer nachgelagerte Analysen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_patients`-Asset liest `data/patients.csv` mit `csv.DictReader`
- [ ] Daten werden ueber `postgres.load_rows()` in die `patients`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Patienten
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A

---

### US-03: raw_visits-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `visits.csv` in PostgreSQL laedt,
**damit** Besuchsdaten fuer Wiederaufnahme-Erkennung und Abteilungsmetriken verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_visits`-Asset liest `data/visits.csv` mit `csv.DictReader`
- [ ] Daten werden ueber `postgres.load_rows()` in die `visits`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Besuche
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer B

---

### US-04: raw_diagnoses-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `diagnoses.csv` in PostgreSQL laedt,
**damit** Diagnosedaten fuer Abteilungsmetriken und Analysen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_diagnoses`-Asset liest `data/diagnoses.csv` mit `csv.DictReader`
- [ ] Daten werden ueber `postgres.load_rows()` in die `diagnoses`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Diagnosen
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer A

---

### US-05: raw_prescriptions-Asset implementieren

**Als** Data Engineer
**moechte ich** ein Dagster-Asset, das `prescriptions.csv` in PostgreSQL laedt,
**damit** Verschreibungsdaten fuer Patientenzusammenfassungen verfuegbar sind.

**Akzeptanzkriterien:**
- [ ] `raw_prescriptions`-Asset liest `data/prescriptions.csv` mit `csv.DictReader`
- [ ] Daten werden ueber `postgres.load_rows()` in die `prescriptions`-Tabelle eingefuegt
- [ ] Asset gibt `MaterializeResult` mit `row_count`-Metadaten zurueck
- [ ] Asset protokolliert die Anzahl der geladenen Verschreibungen
- [ ] Asset gehoert zur Gruppe `raw_ingestion`
- [ ] Zugehoerige Tests bestehen

**Story Points:** 2 (klein)
**Prioritaet:** Must Have
**Vorgeschlagene Zuweisung:** Data Engineer B

---

## Epic 3: Klinische Transformationen

### US-06: patient_summaries-Asset implementieren

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

### US-07: readmission_flags-Asset implementieren

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

### US-08: department_metrics-Asset implementieren

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

## Epic 4: Orchestrierung

### US-09: weekly_analytics_schedule implementieren

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

### US-10: End-to-End-Pipeline-Test in Dagit

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

## Epic 5: Dokumentation & Demo

### US-11: Architecture Decision Records schreiben

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

### US-12: Live-Demo in Dagit vorbereiten

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
| US-01 | PostgresResource implementieren          | 3      | Must Have     | 1    |
| US-02 | raw_patients-Asset implementieren        | 2      | Must Have     | 2    |
| US-03 | raw_visits-Asset implementieren          | 2      | Must Have     | 2    |
| US-04 | raw_diagnoses-Asset implementieren       | 2      | Must Have     | 2    |
| US-05 | raw_prescriptions-Asset implementieren   | 2      | Must Have     | 2    |
| US-06 | patient_summaries-Asset implementieren   | 5      | Must Have     | 3    |
| US-07 | readmission_flags-Asset implementieren   | 5      | Must Have     | 3    |
| US-08 | department_metrics-Asset implementieren  | 5      | Must Have     | 3    |
| US-09 | weekly_analytics_schedule                | 3      | Must Have     | 4    |
| US-10 | End-to-End-Pipeline-Test                 | 3      | Must Have     | 4    |
| US-11 | Architecture Decision Records            | 3      | Should Have   | 5    |
| US-12 | Live-Demo in Dagit vorbereiten           | 3      | Must Have     | 5    |
| **Gesamt** |                                     | **38** |               |      |

---

## Fortgeschrittene / Erweiterungs-Stories

> Die folgenden Stories sind **optional** und fuer fortgeschrittene Studierende oder Teams gedacht, die die Kern-Pipeline vor dem Zeitplan abgeschlossen haben. Sie sind **nicht erforderlich** fuer die Capstone-Bewertung.

---

### Epic 6: Fortgeschritten -- Pandas-Integration (Optional)

### US-13: Datenaufnahme auf pandas umstellen

**Als** Data Engineer mit pandas-Erfahrung
**moechte ich** `csv.DictReader` + `load_rows()` durch pandas DataFrames ersetzen,
**damit** ich pandas fuer Datenvalidierung und -transformation vor dem Laden nutzen kann.

**Akzeptanzkriterien:**
- [ ] pandas als optionale Abhaengigkeit installieren: `uv add pandas` (bereits ueber `[project.optional-dependencies]` in `pyproject.toml` verfuegbar)
- [ ] Eine `load_dataframe(df, table_name)`-Methode zu `PostgresResource` hinzufuegen, die einen pandas DataFrame akzeptiert
- [ ] Roh-Aufnahme-Assets auf `pd.read_csv()` und `postgres.load_dataframe()` umstellen
- [ ] Alle bestehenden Tests bestehen weiterhin
- [ ] Keine Aenderung am Asset-Abhaengigkeitsgraphen oder der oeffentlichen Schnittstelle

**Story Points:** 3 (mittel)
**Prioritaet:** Could Have
**Vorgeschlagene Zuweisung:** Fortgeschrittener Studierender

---

### Epic 7: Fortgeschritten -- AWS-Deployment (Optional)

> Siehe [AWS_DEPLOYMENT_DE.md](AWS_DEPLOYMENT_DE.md) fuer die vollstaendige Schritt-fuer-Schritt-Anleitung.

### US-14: Pipeline auf AWS deployen (EC2 + RDS)

**Als** Data Engineer mit AWS-Erfahrung
**moechte ich** die ClinicFlow-Pipeline auf EC2 mit einem RDS-PostgreSQL-Backend deployen,
**damit** die Pipeline in einer produktionsaehnlichen Cloud-Umgebung laeuft.

**Akzeptanzkriterien:**
- [ ] Eine RDS-PostgreSQL-`db.t3.micro`-Instanz ist provisioniert (Free Tier)
- [ ] Das Datenbankschema (`db/init.sql`) ist auf der RDS-Instanz angewendet
- [ ] Eine EC2-`t3.micro`-Instanz ist gestartet und mit Python, uv und dem Projekt konfiguriert
- [ ] CSV-Datendateien sind in einen S3-Bucket hochgeladen
- [ ] Umgebungsvariablen (DB-Host, Zugangsdaten, S3-Bucket) sind ueber `.env` konfiguriert
- [ ] `dg dev` laeuft auf EC2 und die Dagit-UI ist ueber die oeffentliche IP der Instanz erreichbar
- [ ] Alle Assets koennen gegen die RDS-Datenbank materialisiert werden
- [ ] Alle Ressourcen werden nach der Demo abgebaut, um Kosten zu vermeiden

**Story Points:** 5 (gross)
**Prioritaet:** Could Have
**Vorgeschlagene Zuweisung:** Fortgeschrittener Studierender / Team mit AWS-Erfahrung

---

### US-15: CSV-Aufnahme fuer S3 anpassen

**Als** Data Engineer
**moechte ich**, dass die Roh-Aufnahme-Assets CSV-Dateien aus S3 statt vom lokalen Dateisystem lesen,
**damit** die Pipeline in einem Cloud-nativen Deployment funktioniert.

**Akzeptanzkriterien:**
- [ ] `boto3` ist als Abhaengigkeit hinzugefuegt (`uv add boto3`)
- [ ] Eine Hilfsfunktion liest CSV-Dateien aus S3 mit `boto3` und gibt eine Liste von Dicts zurueck
- [ ] Roh-Aufnahme-Assets erkennen anhand einer Umgebungsvariable, ob von lokalem `data/` oder S3 gelesen werden soll
- [ ] Die Pipeline funktioniert sowohl lokal (CSV-Dateien) als auch auf AWS (S3)
- [ ] Alle bestehenden Tests bestehen weiterhin (sie erfordern keinen S3-Zugriff)

**Story Points:** 3 (mittel)
**Prioritaet:** Could Have
**Vorgeschlagene Zuweisung:** Fortgeschrittener Studierender

---

## Erweiterte Uebersichtstabelle (einschliesslich fortgeschrittener Stories)

| ID    | Titel                                    | Punkte | Prioritaet    | Epic | Pflicht  |
|-------|------------------------------------------|--------|---------------|------|----------|
| US-01 | PostgresResource implementieren          | 3      | Must Have     | 1    | Ja       |
| US-02 | raw_patients-Asset implementieren        | 2      | Must Have     | 2    | Ja       |
| US-03 | raw_visits-Asset implementieren          | 2      | Must Have     | 2    | Ja       |
| US-04 | raw_diagnoses-Asset implementieren       | 2      | Must Have     | 2    | Ja       |
| US-05 | raw_prescriptions-Asset implementieren   | 2      | Must Have     | 2    | Ja       |
| US-06 | patient_summaries-Asset implementieren   | 5      | Must Have     | 3    | Ja       |
| US-07 | readmission_flags-Asset implementieren   | 5      | Must Have     | 3    | Ja       |
| US-08 | department_metrics-Asset implementieren  | 5      | Must Have     | 3    | Ja       |
| US-09 | weekly_analytics_schedule                | 3      | Must Have     | 4    | Ja       |
| US-10 | End-to-End-Pipeline-Test                 | 3      | Must Have     | 4    | Ja       |
| US-11 | Architecture Decision Records            | 3      | Should Have   | 5    | Ja       |
| US-12 | Live-Demo in Dagit vorbereiten           | 3      | Must Have     | 5    | Ja       |
| US-13 | Datenaufnahme auf pandas umstellen       | 3      | Could Have    | 6    | Nein     |
| US-14 | Pipeline auf AWS deployen                | 5      | Could Have    | 7    | Nein     |
| US-15 | CSV-Aufnahme fuer S3 anpassen            | 3      | Could Have    | 7    | Nein     |
| **Kern-Gesamt** |                               | **38** |               |      |          |
| **Mit Fortgeschrittenen** |                      | **49** |               |      |          |
