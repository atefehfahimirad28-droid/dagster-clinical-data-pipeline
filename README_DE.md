# Abschlussprojekt: Klinische Analyse-Pipeline

## User Stories

Siehe [USER_STORIES_DE.md](USER_STORIES_DE.md) fuer die vollstaendige Liste der User Stories dieses Projekts.

## Ueberblick

Die **Charite -- Universitaetsmedizin Berlin**, eines der groessten
Universitaetskrankenhaeuser Europas, benoetigt eine woechentliche klinische
Analyse-Pipeline zur Unterstuetzung von Qualitaetsverbesserungsinitiativen und
der Berichterstattung an die Krankenhausleitung. Das klinische
Data-Engineering-Team der Charite muss eine automatisierte Pipeline erstellen, die:

1. **Rohdaten** aus CSV-Exporten aufnimmt (Patienten, Besuche, Diagnosen, Rezepte)
   ueber die drei Charite-Standorte hinweg
2. Die Daten in verwertbare Analysen **transformiert**: Patientenzusammenfassungen,
   Abteilungskennzahlen und Wiederaufnahme-Risikobewertungen
3. Ergebnisse in **PostgreSQL** laedt fuer nachgelagerte Dashboards und Berichte,
   die vom Qualitaetsmanagement und den Abteilungsleitungen der Charite genutzt werden
4. Nach einem **woechentlichen Zeitplan** mit korrekter Fehlerbehandlung und
   Konfiguration laeuft

Alle Patientendaten in diesem Projekt sind **synthetisch und fiktiv**. Es werden
keine echten geschuetzten Gesundheitsinformationen (PHI) verwendet. Die Charite wird
ausschliesslich als Lernkontext referenziert.

## Architektur

```
 CSV-Dateien                Dagster Assets                    PostgreSQL
 (data/)                    (clinicflow)                      (clinicflow DB)

 patients.csv ──> [ raw_patients ] ─────────┐
                                            ├──> [ patient_summaries ] ──> patient_summaries
 visits.csv ───> [ raw_visits ] ────────────┤
                        │                   │
                        ├──> [ readmission_flags ] ──────> readmission_flags
                        │           │
 diagnoses.csv > [ raw_diagnoses ] ─┼───────┴──> [ department_metrics ] ──> department_metrics
                                    │
 prescriptions  [ raw_prescriptions ]
   .csv ──────>         │
                        └────────────────────> (verwendet in patient_summaries)


 Zeitplan: weekly_analytics_schedule (Montags 07:00)
 Jobs:     weekly_analytics_job, readmission_screening_job
```

## Asset-Abhaengigkeitsgraph

```
raw_patients ──────────────┐
                           │
raw_visits ────────────────┼──> patient_summaries
  │                        │
  ├──> readmission_flags ──┘
  │           │
raw_diagnoses ┼──> department_metrics
              │
raw_prescriptions ──> (patient_summaries)
```

## Lernziele (Bloom'sche Taxonomie)

| Stufe | Verb | Lernziel |
|-------|------|----------|
| L2 Verstehen | Erklaeren | Beschreiben, wie Dagster-Assets einen Abhaengigkeitsgraphen bilden |
| L3 Anwenden | Implementieren | CSV-Daten mit Dagster-Assets und -Ressourcen in PostgreSQL laden |
| L4 Analysieren | Aggregieren | Patientenzusammenfassungen durch Kombination mehrerer Datenquellen berechnen |
| L5 Bewerten | Beurteilen | Wiederaufnahmeraten berechnen und Risikopatienten kennzeichnen |
| L5 Bewerten | Einschaetzen | Abteilungs-KPIs ableiten zur Bewertung der klinischen Leistung |
| L6 Erschaffen | Entwerfen | Jobs, Zeitplaene und Konfiguration zu einer vollstaendigen Pipeline verbinden |

## Voraussetzungen

- Dagster-Grundlagen: Assets, Abhaengigkeiten, I/O, Jobs, Fehlerbehandlung (Tage 1-3)
- Zeitplaene, Sensoren, Partitionen, Konfiguration (Tage 4-5)
- Python, SQL Grundlagen
- Docker

## Einrichtungsanleitung

### 1. Infrastruktur starten

```bash
cd capstone-medical
docker compose up -d
```

Dies startet PostgreSQL 17 mit der vorinstallierten `clinicflow`-Datenbank und dem
Schema (simuliert das klinische Data Warehouse der Charite).

### 2. Abhaengigkeiten installieren

```bash
cd clinicflow
uv sync
```

### 3. Tests ausfuehren (TDD)

```bash
uv run pytest tests/ -v
```

Alle Tests werden anfangs fehlschlagen. Ihre Aufgabe ist es, die TODO-Stubs zu
implementieren, damit die Tests bestehen.

### 4. Dagster-Entwicklungsserver starten

```bash
dg dev
```

Oeffnen Sie [http://localhost:3000](http://localhost:3000), um die Dagit-Oberflaeche
anzuzeigen.

## Aufgabenaufteilung

Arbeiten Sie die TODOs in dieser Reihenfolge ab. Fuehren Sie nach jeder Aufgabe
`uv run pytest tests/ -v` aus, um Ihren Fortschritt zu ueberpruefen.

### Aufgabe 1: PostgreSQL-Ressource konfigurieren (L3)
**Datei:** `src/clinicflow/defs/resources.py`

Implementieren Sie die `PostgresResource`-Methoden:
- `get_connection()` -- eine psycopg2-Verbindung zurueckgeben
- `execute_query(query, params)` -- eine SQL-Anweisung ausfuehren
- `load_rows(rows, table_name)` -- eine Liste von Dicts per Bulk-Insert einfuegen

### Aufgabe 2: Rohdaten-Ingestion-Assets implementieren (L3)
**Datei:** `src/clinicflow/defs/assets.py`

Implementieren Sie die vier `raw_*`-Assets. Jedes soll:
- Seine CSV-Datei mit `csv.DictReader` einlesen
- Zeilen in die entsprechende PostgreSQL-Tabelle einfuegen
- Metadaten zurueckgeben (Zeilenanzahl)

### Aufgabe 3: Wiederaufnahme-Flags implementieren (L5)
**Datei:** `src/clinicflow/defs/assets.py`

Implementieren Sie `readmission_flags`:
- Besuche nach Patient und Aufnahmedatum abfragen und sortieren
- Paare kennzeichnen, bei denen ein Patient innerhalb des konfigurierbaren
  Zeitfensters (Standard: 30 Tage) wieder aufgenommen wurde
- Flags in die `readmission_flags`-Tabelle einfuegen

### Aufgabe 4: Patientenzusammenfassungen implementieren (L4)
**Datei:** `src/clinicflow/defs/assets.py`

Implementieren Sie `patient_summaries`:
- Pro Patient aggregieren: Gesamtbesuche, durchschnittliche Aufenthaltsdauer,
  letzter Besuch, Hauptabteilung, Anzahl aktiver Rezepte
- Risikokategorie basierend auf Besuchshaeufigkeit und Wiederaufnahmehistorie zuweisen

### Aufgabe 5: Abteilungskennzahlen implementieren (L5)
**Datei:** `src/clinicflow/defs/assets.py`

Implementieren Sie `department_metrics`:
- Besuche nach Abteilung gruppieren
- Berechnen: Gesamtaufnahmen, durchschnittliche Aufenthaltsdauer,
  Wiederaufnahmeanzahl/-rate, haeufigster Diagnosecode
- In die `department_metrics`-Tabelle einfuegen

### Aufgabe 6: Job und Zeitplan konfigurieren (L6)
**Datei:** `src/clinicflow/defs/jobs.py` und `src/clinicflow/defs/schedules.py`

- `weekly_analytics_job` definieren, der alle Assets auswaehlt
- `readmission_screening_job` fuer Wiederaufnahme- und Patientenzusammenfassungs-Assets
- Woechentlichen Zeitplan erstellen, der jeden Montag um 07:00 Uhr laeuft

## Definition of Done

Ihre Arbeit gilt als abgeschlossen, wenn:

1. Alle Tests bestehen (`uv run pytest tests/ -v`)
2. Der Code in den `main`-Branch gemergt wurde
3. CI-Checks bestehen (Conventional Commits + Ruff-Linting)

### Branching-Strategie

Halten Sie es einfach -- erstellen Sie **einen Feature-Branch**, arbeiten
Sie dort und oeffnen Sie dann einen Pull Request zum Mergen in `main`:

```bash
git checkout -b feature/postgres-resource   # Feature-Branch erstellen
# ... implementieren, committen, pushen ...
git push -u origin feature/postgres-resource  # zu GitHub pushen
# PR auf GitHub oeffnen -> mergen, wenn CI gruen ist
```

Beispiel-Branch-Namen: `feature/postgres-resource`, `feature/raw-ingestion`,
`feature/readmission-flags`, `feature/department-metrics`.

## Erwartete Ergebnisse

1. Alle Tests bestanden (`uv run pytest tests/ -v`)
2. Vollstaendiger Asset-Graph sichtbar in der Dagit-Oberflaeche
3. Erfolgreiche Materialisierung aller Assets gegen die Docker-PostgreSQL-Instanz
4. Woechentlicher Zeitplan registriert und sichtbar in Dagit

## Bewertungskriterien

| Kriterium | Gewichtung |
|-----------|------------|
| Alle 12 Tests bestanden | 30% |
| Assets materialisieren fehlerfrei in Dagit | 25% |
| Korrekte Asset-Abhaengigkeiten (Graphstruktur) | 15% |
| Wiederaufnahme-Erkennungslogik ist korrekt | 15% |
| Zeitplan und Jobs korrekt konfiguriert | 10% |
| Code-Qualitaet (Fehlerbehandlung, Logging, Docstrings) | 5% |

## Hinweis zum Datenschutz

Alle Patientennamen, medizinischen Daten und klinischen Aufzeichnungen in diesem
Projekt sind **vollstaendig fiktiv und synthetisch generiert** fuer
Ausbildungszwecke. Es werden keine echten geschuetzten Gesundheitsinformationen
(PHI) verwendet. Dieses Projekt unterliegt nicht der HIPAA-Regulierung, da es
keine echten Patientendaten enthaelt. Die Referenz auf die Charite --
Universitaetsmedizin Berlin dient ausschliesslich dem Lernkontext und stellt
keine tatsaechlichen Charite-Daten oder -Systeme dar.

## AWS-Bereitstellung (Optional)

Fuer Studierende mit AWS-Erfahrung siehe
[AWS_DEPLOYMENT_DE.md](AWS_DEPLOYMENT_DE.md) fuer eine Schritt-fuer-Schritt-Anleitung
zur Bereitstellung dieser Pipeline auf EC2 + RDS mit dem AWS Free Tier.
