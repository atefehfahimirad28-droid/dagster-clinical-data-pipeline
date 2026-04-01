# """Dagster assets for the Charite Clinical Analytics Pipeline.

# Students implement the TODO stubs to build the complete asset graph:

#     raw_patients ──────────────┐
#                                │
#     raw_visits ────────────────┼──> patient_summaries
#       │                        │
#       ├──> readmission_flags ──┘
#       │           │
#     raw_diagnoses ┼──> department_metrics
#                   │
#     raw_prescriptions ──> (patient_summaries)

# All data is synthetic/fictional. No real PHI is used.

# German: Dagster-Assets fuer die klinische Analyse-Pipeline der Charite.

# Studierende implementieren die TODO-Stubs, um den vollstaendigen
# Asset-Graphen zu erstellen. Alle Daten sind synthetisch/fiktiv.
# Es werden keine echten Patientendaten (PHI) verwendet.
# """

# import csv
# from datetime import datetime, date
# from pathlib import Path
# from collections import defaultdict
# from typing import Any

# import dagster as dg

# from clinicflow.defs.resources import PostgresResource

# # ---------------------------------------------------------------------------
# # Helper: locate the data/ directory (two levels up from this file)
# # DE: Hilfsfunktion: das data/-Verzeichnis lokalisieren (zwei Ebenen ueber dieser Datei)
# # ---------------------------------------------------------------------------
# DATA_DIR = Path(__file__).resolve().parents[4] / "data"


# # ---------------------------------------------------------------------------
# # Pure helper functions (tested independently)
# # DE: Reine Hilfsfunktionen (unabhaengig getestet)
# # ---------------------------------------------------------------------------


# def detect_readmissions(
#     visits: list[dict],
#     window_days: int = 30,
# ) -> list[dict]:
#     """Detect readmissions within a configurable window.

#     Given a list of visit dicts sorted by patient_id and admission_date,
#     return a list of readmission flag dicts for any pair of consecutive
#     visits by the same patient where the second admission is within
#     window_days of the first discharge.

#     Args:
#         visits: List of dicts with keys: visit_id, patient_id,
#                 department, admission_date, discharge_date
#                 (dates as datetime.date or datetime objects)
#         window_days: Maximum days between discharge and next admission
#                      to count as a readmission (default 30)

#     Returns:
#         List of dicts with keys: patient_id, original_visit_id,
#         readmission_visit_id, days_between, department

#     DE: Wiederaufnahmen innerhalb eines konfigurierbaren Zeitfensters erkennen.

#     Erhaelt eine Liste von Besuchs-Dicts, sortiert nach Patienten-ID und Aufnahmedatum,
#     und gibt eine Liste von Wiederaufnahme-Flags fuer aufeinanderfolgende Besuche
#     desselben Patienten zurueck, bei denen die zweite Aufnahme innerhalb von
#     window_days nach der ersten Entlassung liegt.
#     """
#     flags = []
    
#     try:
#         sorted_visits = sorted(visits, key=lambda v: (v['patient_id'], v['admission_date']))
        
#         for i in range(len(sorted_visits) - 1):
#             current = sorted_visits[i]
#             next_visit = sorted_visits[i + 1]
            
#             if current['patient_id'] == next_visit['patient_id']:
#                 if isinstance(current['discharge_date'], str):
#                     discharge = datetime.strptime(current['discharge_date'], '%Y-%m-%d').date()
#                     admission = datetime.strptime(next_visit['admission_date'], '%Y-%m-%d').date()
#                 else:
#                     discharge = current['discharge_date']
#                     admission = next_visit['admission_date']
                
#                 days_between = (admission - discharge).days
                
#                 if days_between <= window_days:
#                     flags.append({
#                         'patient_id': current['patient_id'],
#                         'original_visit_id': current['visit_id'],
#                         'readmission_visit_id': next_visit['visit_id'],
#                         'days_between': days_between,
#                         'department': next_visit.get('department', 'Unknown')
#                     })
#     except Exception as e:
#         raise Exception(f"Error detecting readmissions: {str(e)}")
    
#     return flags


# def calculate_avg_stay(
#     admission_date: datetime,
#     discharge_date: datetime,
# ) -> float:
#     """Calculate length of stay in days.

#     Args:
#         admission_date: Date of admission
#         discharge_date: Date of discharge

#     Returns:
#         Number of days as a float (discharge - admission).days
#         Returns 0.0 if discharge_date is None or before admission_date.

#     DE: Berechnet die Aufenthaltsdauer in Tagen.

#     Gibt die Anzahl der Tage als Float zurueck (Entlassung - Aufnahme).days.
#     Gibt 0.0 zurueck, wenn das Entlassungsdatum None oder vor dem Aufnahmedatum liegt.
#     """
#     try:
#         if discharge_date is None or discharge_date < admission_date:
#             return 0.0
        
#         if isinstance(admission_date, str):
#             admission = datetime.strptime(admission_date, '%Y-%m-%d')
#         else:
#             admission = admission_date
            
#         if isinstance(discharge_date, str):
#             discharge = datetime.strptime(discharge_date, '%Y-%m-%d')
#         else:
#             discharge = discharge_date
        
#         return float((discharge - admission).days)
#     except Exception as e:
#         raise Exception(f"Error calculating average stay: {str(e)}")


# # ---------------------------------------------------------------------------
# # Raw ingestion assets (L3 Apply)
# # DE: Rohdaten-Aufnahme-Assets (L3 Anwenden)
# # ---------------------------------------------------------------------------


# @dg.asset(
#     group_name="raw_ingestion",
#     kinds={"python", "postgres"},
# )
# def raw_patients(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Load patients.csv into the patients table.

#     Steps:
#         1. Read data/patients.csv with csv.DictReader
#         2. Use postgres.load_rows() to insert into 'patients' table
#         3. Return MaterializeResult with row_count metadata

#     DE: Laedt patients.csv in die Patienten-Tabelle.
#     """
#     try:
#         context.log.info("📂 Reading patients.csv...")
#         with open(DATA_DIR / "patients.csv", newline="") as f:
#             rows = list(csv.DictReader(f))
        
#         context.log.info(f"✅ Loaded {len(rows)} patient records from CSV")
        
#         count = postgres.load_rows(rows, "patients")
        
#         context.log.info(f"💾 Successfully inserted {count} patients into database")
#         context.log.info(f"📊 Patient Data Summary:")
#         context.log.info(f"   └─ Total patients: {count}")
#         context.log.info(f"   └─ Columns: {', '.join(rows[0].keys()) if rows else 'None'}")
        
#         return dg.MaterializeResult(metadata={"row_count": count})
#     except FileNotFoundError as e:
#         context.log.error(f"❌ Patients CSV file not found: {str(e)}")
#         context.log.error(f"   Expected path: {DATA_DIR / 'patients.csv'}")
#         raise
#     except Exception as e:
#         context.log.error(f"❌ Error loading patients: {str(e)}")
#         raise


# @dg.asset(
#     group_name="raw_ingestion",
#     kinds={"python", "postgres"},
# )
# def raw_visits(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Load visits.csv into the visits table.

#     Steps:
#         1. Read data/visits.csv with csv.DictReader
#         2. Use postgres.load_rows() to insert into 'visits' table
#         3. Return MaterializeResult with row_count metadata

#     DE: Laedt visits.csv in die Besuche-Tabelle.
#     """
#     try:
#         context.log.info("📂 Reading visits.csv...")
#         with open(DATA_DIR / "visits.csv", newline="") as f:
#             rows = list(csv.DictReader(f))
        
#         context.log.info(f"✅ Loaded {len(rows)} visit records from CSV")
        
#         count = postgres.load_rows(rows, "visits")
        
#         context.log.info(f"💾 Successfully inserted {count} visits into database")
#         context.log.info(f"📊 Visit Data Summary:")
#         context.log.info(f"   └─ Total visits: {count}")
#         context.log.info(f"   └─ Date range: {rows[0]['admission_date']} to {rows[-1]['admission_date']}")
        
#         return dg.MaterializeResult(metadata={"row_count": count})
#     except FileNotFoundError as e:
#         context.log.error(f"❌ Visits CSV file not found: {str(e)}")
#         context.log.error(f"   Expected path: {DATA_DIR / 'visits.csv'}")
#         raise
#     except Exception as e:
#         context.log.error(f"❌ Error loading visits: {str(e)}")
#         raise


# @dg.asset(
#     group_name="raw_ingestion",
#     kinds={"python", "postgres"},
# )
# def raw_diagnoses(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Load diagnoses.csv into the diagnoses table.

#     Steps:
#         1. Read data/diagnoses.csv with csv.DictReader
#         2. Use postgres.load_rows() to insert into 'diagnoses' table
#         3. Return MaterializeResult with row_count metadata

#     DE: Laedt diagnoses.csv in die Diagnose-Tabelle.
#     """
#     try:
#         context.log.info("📂 Reading diagnoses.csv...")
#         with open(DATA_DIR / "diagnoses.csv", newline="") as f:
#             rows = list(csv.DictReader(f))
        
#         context.log.info(f"✅ Loaded {len(rows)} diagnosis records from CSV")
        
#         count = postgres.load_rows(rows, "diagnoses")
        
#         context.log.info(f"💾 Successfully inserted {count} diagnoses into database")
        
#         # Calculate severity distribution
#         severity_counts = defaultdict(int)
#         for row in rows:
#             severity_counts[row.get('severity_level', 'Unknown')] += 1
        
#         context.log.info(f"📊 Diagnosis Data Summary:")
#         context.log.info(f"   └─ Total diagnoses: {count}")
#         context.log.info(f"   └─ Severity distribution: {dict(severity_counts)}")
        
#         return dg.MaterializeResult(metadata={"row_count": count})
#     except FileNotFoundError as e:
#         context.log.error(f"❌ Diagnoses CSV file not found: {str(e)}")
#         context.log.error(f"   Expected path: {DATA_DIR / 'diagnoses.csv'}")
#         raise
#     except Exception as e:
#         context.log.error(f"❌ Error loading diagnoses: {str(e)}")
#         raise


# @dg.asset(
#     group_name="raw_ingestion",
#     kinds={"python", "postgres"},
#     deps=[raw_visits],
# )
# def raw_prescriptions(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Load prescriptions.csv into the prescriptions table.

#     Steps:
#         1. Read data/prescriptions.csv with csv.DictReader
#         2. Use postgres.load_rows() to insert into 'prescriptions' table
#         3. Return MaterializeResult with row_count metadata

#     DE: Laedt prescriptions.csv in die Verschreibungs-Tabelle.
#     """
#     try:
#         context.log.info("📂 Reading prescriptions.csv...")
#         with open(DATA_DIR / "prescriptions.csv", newline="") as f:
#             rows = list(csv.DictReader(f))
        
#         context.log.info(f"✅ Loaded {len(rows)} prescription records from CSV")
        
#         # Convert empty end_date to NULL
#         empty_end_date_count = 0
#         for row in rows:
#             if row.get('end_date') == '':
#                 row['end_date'] = None
#                 empty_end_date_count += 1
        
#         if empty_end_date_count > 0:
#             context.log.info(f"🔄 Converted {empty_end_date_count} empty end_date fields to NULL")
        
#         # Verify all visit_ids exist before inserting
#         all_visit_ids = [row['visit_id'] for row in rows]
#         placeholders = ','.join(['%s'] * len(all_visit_ids))
#         existing_visits = postgres.execute_query(
#             f"SELECT visit_id FROM visits WHERE visit_id IN ({placeholders})",
#             tuple(all_visit_ids)
#         )
#         existing_visit_ids = {row[0] for row in existing_visits}
        
#         # Filter rows to only those with valid visit_ids
#         valid_rows = [row for row in rows if row['visit_id'] in existing_visit_ids]
        
#         if len(valid_rows) < len(rows):
#             missing_count = len(rows) - len(valid_rows)
#             context.log.warning(f"⚠️  Skipping {missing_count} prescriptions with missing visit references")
            
#             # Log the missing visit_ids for debugging
#             missing_visits = [row['visit_id'] for row in rows if row['visit_id'] not in existing_visit_ids]
#             context.log.debug(f"   Missing visit IDs: {', '.join(set(missing_visits))}")
        
#         if valid_rows:
#             count = postgres.load_rows(valid_rows, "prescriptions")
#             context.log.info(f"💾 Successfully inserted {count} prescriptions into database")
            
#             # Calculate medication distribution
#             medication_counts = defaultdict(int)
#             for row in valid_rows:
#                 medication_counts[row.get('medication_name', 'Unknown')] += 1
            
#             context.log.info(f"📊 Prescription Data Summary:")
#             context.log.info(f"   └─ Total prescriptions loaded: {count}")
#             context.log.info(f"   └─ Active prescriptions (no end date): {sum(1 for row in valid_rows if row['end_date'] is None)}")
#             context.log.info(f"   └─ Top 3 medications: {dict(sorted(medication_counts.items(), key=lambda x: x[1], reverse=True)[:3])}")
#         else:
#             count = 0
#             context.log.warning("⚠️  No valid prescriptions to load")
        
#         return dg.MaterializeResult(metadata={"row_count": count})
#     except FileNotFoundError as e:
#         context.log.error(f"❌ Prescriptions CSV file not found: {str(e)}")
#         context.log.error(f"   Expected path: {DATA_DIR / 'prescriptions.csv'}")
#         raise
#     except Exception as e:
#         context.log.error(f"❌ Error loading prescriptions: {str(e)}")
#         raise


# # ---------------------------------------------------------------------------
# # Readmission flags (L5 Evaluate)
# # DE: Wiederaufnahme-Flags (L5 Bewerten)
# # ---------------------------------------------------------------------------


# @dg.asset(
#     deps=[raw_visits],
#     group_name="analytics",
#     kinds={"python", "postgres"},
# )
# def readmission_flags(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Flag patients readmitted within a configurable window (default 30 days).

#     This asset depends on raw_visits.

#     Steps:
#         1. Query all completed visits ordered by patient_id, admission_date
#         2. Use detect_readmissions() helper with the configured window
#         3. Insert flags into readmission_flags table
#         4. Return MaterializeResult with flag_count metadata

#     Configuration:
#         The readmission window (in days) can be configured. Default is 30.

#     DE: Patienten markieren, die innerhalb eines konfigurierbaren Zeitfensters
#     (Standard 30 Tage) wieder aufgenommen wurden. Dieses Asset haengt von raw_visits ab.
#     """
#     try:
#         context.log.info("🔍 Analyzing visits for readmission patterns...")
        
#         visits_data = postgres.execute_query(
#             "SELECT visit_id, patient_id, department, admission_date, "
#             "discharge_date FROM visits WHERE status = 'completed' "
#             "ORDER BY patient_id, admission_date"
#         )
        
#         context.log.info(f"📊 Retrieved {len(visits_data)} completed visits from database")
        
#         visit_dicts = []
#         for row in visits_data:
#             visit_dicts.append({
#                 'visit_id': row[0],
#                 'patient_id': row[1],
#                 'department': row[2],
#                 'admission_date': row[3],
#                 'discharge_date': row[4]
#             })
        
#         flags = detect_readmissions(visit_dicts, window_days=30)
        
#         if flags:
#             flag_count = postgres.load_rows(flags, "readmission_flags")
#             context.log.info(f"🏥 Detected {flag_count} readmission cases")
            
#             # Calculate department distribution of readmissions
#             dept_counts = defaultdict(int)
#             for flag in flags:
#                 dept_counts[flag['department']] += 1
            
#             context.log.info(f"📊 Readmission Analysis:")
#             context.log.info(f"   └─ Total readmissions: {flag_count}")
#             context.log.info(f"   └─ Readmission window: 30 days")
#             context.log.info(f"   └─ Departments with most readmissions: {dict(sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)[:3])}")
            
#             # Calculate average days between readmissions
#             avg_days = sum(flag['days_between'] for flag in flags) / len(flags)
#             context.log.info(f"   └─ Average days between readmissions: {avg_days:.1f} days")
#         else:
#             flag_count = 0
#             context.log.info("✅ No readmissions detected within the 30-day window")
        
#         return dg.MaterializeResult(metadata={"flag_count": flag_count})
#     except Exception as e:
#         context.log.error(f"❌ Error detecting readmission flags: {str(e)}")
#         raise


# # ---------------------------------------------------------------------------
# # Patient summaries (L4 Analyze)
# # DE: Patientenzusammenfassungen (L4 Analysieren)
# # ---------------------------------------------------------------------------


# @dg.asset(
#     deps=[raw_patients, raw_visits, raw_prescriptions],
#     group_name="analytics",
#     kinds={"python", "postgres"},
# )
# def patient_summaries(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Aggregate per-patient statistics.

#     Depends on raw_patients, raw_visits, and raw_prescriptions.

#     Computes for each patient:
#         - total_visits: count of all visits
#         - last_visit_date: most recent admission date
#         - primary_department: department with most visits
#         - avg_stay_days: average length of stay across all visits
#         - active_prescriptions: count of prescriptions with no end_date
#           or end_date in the future
#         - risk_category: 'high' if total_visits >= 5 or has readmission,
#                          'medium' if total_visits >= 3,
#                          'low' otherwise

#     Steps:
#         1. Query patients, visits, and prescriptions from PostgreSQL
#         2. Compute aggregations using plain Python (list comprehensions, dicts) or SQL
#         3. Insert results into patient_summaries table
#         4. Return MaterializeResult with patient_count metadata

#     DE: Aggregierte Statistiken pro Patient berechnen.

#     Berechnet fuer jeden Patienten: Gesamtbesuche, letztes Besuchsdatum,
#     Hauptabteilung, durchschnittliche Aufenthaltsdauer, aktive Verschreibungen
#     und Risikokategorie.
#     """
#     try:
#         context.log.info("📊 Generating patient summary analytics...")
        
#         patients = postgres.execute_query("SELECT patient_id FROM patients")
#         context.log.info(f"👥 Processing {len(patients)} patients")
        
#         visits = postgres.execute_query(
#             "SELECT patient_id, department, admission_date, discharge_date "
#             "FROM visits WHERE status = 'completed'"
#         )
#         context.log.info(f"📋 Retrieved {len(visits)} visit records")
        
#         prescriptions = postgres.execute_query(
#             "SELECT patient_id, end_date FROM prescriptions"
#         )
#         context.log.info(f"💊 Retrieved {len(prescriptions)} prescription records")
        
#         readmissions = postgres.execute_query(
#             "SELECT patient_id FROM readmission_flags"
#         )
        
#         readmission_patients = {row[0] for row in readmissions}
#         if readmission_patients:
#             context.log.info(f"⚠️  {len(readmission_patients)} patients have readmission flags")
        
#         patient_visits = defaultdict(list)
#         for visit in visits:
#             patient_id = visit[0]
#             patient_visits[patient_id].append({
#                 'department': visit[1],
#                 'admission_date': visit[2],
#                 'discharge_date': visit[3]
#             })
        
#         summaries = []
#         risk_distribution = defaultdict(int)
        
#         for patient_row in patients:
#             patient_id = patient_row[0]
#             visits_list = patient_visits.get(patient_id, [])
            
#             total_visits = len(visits_list)
            
#             if visits_list:
#                 last_visit = max(v['admission_date'] for v in visits_list)
#                 last_visit_date = last_visit
#             else:
#                 last_visit_date = None
            
#             if visits_list:
#                 dept_counts = defaultdict(int)
#                 for v in visits_list:
#                     dept_counts[v['department']] += 1
#                 primary_department = max(dept_counts, key=dept_counts.get)
#             else:
#                 primary_department = None
            
#             stay_days = []
#             for v in visits_list:
#                 stay = calculate_avg_stay(v['admission_date'], v['discharge_date'])
#                 stay_days.append(stay)
#             avg_stay = sum(stay_days) / len(stay_days) if stay_days else 0.0
            
#             active_count = 0
#             for presc in prescriptions:
#                 if presc[0] == patient_id:
#                     end_date = presc[1]
#                     if end_date is None or end_date > datetime.now().date():
#                         active_count += 1
            
#             if total_visits >= 5 or patient_id in readmission_patients:
#                 risk_category = 'high'
#             elif total_visits >= 3:
#                 risk_category = 'medium'
#             else:
#                 risk_category = 'low'
            
#             risk_distribution[risk_category] += 1
            
#             summaries.append({
#                 'patient_id': patient_id,
#                 'total_visits': total_visits,
#                 'last_visit_date': last_visit_date,
#                 'primary_department': primary_department,
#                 'avg_stay_days': round(avg_stay, 2),
#                 'active_prescriptions': active_count,
#                 'risk_category': risk_category
#             })
        
#         if summaries:
#             count = postgres.load_rows(summaries, "patient_summaries")
#             context.log.info(f"✅ Created {count} patient summaries")
            
#             context.log.info(f"📊 Patient Risk Distribution:")
#             context.log.info(f"   └─ High risk: {risk_distribution['high']} patients")
#             context.log.info(f"   └─ Medium risk: {risk_distribution['medium']} patients")
#             context.log.info(f"   └─ Low risk: {risk_distribution['low']} patients")
            
#             # Calculate average metrics
#             avg_visits = sum(s['total_visits'] for s in summaries) / len(summaries)
#             avg_active_rx = sum(s['active_prescriptions'] for s in summaries) / len(summaries)
#             context.log.info(f"📈 Average Metrics:")
#             context.log.info(f"   └─ Visits per patient: {avg_visits:.1f}")
#             context.log.info(f"   └─ Active prescriptions per patient: {avg_active_rx:.1f}")
#         else:
#             count = 0
#             context.log.warning("⚠️  No patient summaries generated")
        
#         return dg.MaterializeResult(metadata={"patient_count": count})
#     except Exception as e:
#         context.log.error(f"❌ Error creating patient summaries: {str(e)}")
#         raise


# # ---------------------------------------------------------------------------
# # Department metrics (L5 Evaluate)
# # DE: Abteilungskennzahlen (L5 Bewerten)
# # ---------------------------------------------------------------------------


# @dg.asset(
#     deps=[raw_visits, raw_diagnoses, readmission_flags],
#     group_name="analytics",
#     kinds={"python", "postgres"},
# )
# def department_metrics(
#     context: dg.AssetExecutionContext,
#     postgres: PostgresResource,
# ) -> dg.MaterializeResult:
#     """Calculate per-department performance KPIs.

#     Depends on raw_visits, raw_diagnoses, and readmission_flags.

#     Computes for each department:
#         - total_admissions: count of visits
#         - avg_stay_days: average length of stay
#         - readmission_count: number of readmission flags
#         - readmission_rate: readmission_count / total_admissions
#         - top_diagnosis_code: most frequent diagnosis code
#         - bed_utilization_rate: placeholder (set to 0.75 or compute if desired)
#         - reporting_period: current year-month or 'all-time'

#     Steps:
#         1. Query visits, diagnoses, and readmission_flags
#         2. Group by department and compute metrics
#         3. Insert into department_metrics table
#         4. Return MaterializeResult with department_count metadata

#     DE: Leistungskennzahlen (KPIs) pro Abteilung berechnen.

#     Berechnet fuer jede Abteilung: Gesamtaufnahmen, durchschnittliche
#     Aufenthaltsdauer, Wiederaufnahmeanzahl, Wiederaufnahmerate,
#     haeufigster Diagnosecode und Bettenauslastungsrate.
#     """
#     try:
#         context.log.info("🏥 Calculating department performance metrics...")
        
#         visits_data = postgres.execute_query(
#             "SELECT department, diagnosis_code, admission_date, discharge_date "
#             "FROM visits WHERE status = 'completed'"
#         )
#         context.log.info(f"📊 Retrieved {len(visits_data)} visits for analysis")
        
#         readmissions_data = postgres.execute_query(
#             "SELECT department FROM readmission_flags"
#         )
#         context.log.info(f"🏥 Retrieved {len(readmissions_data)} readmission records")
        
#         dept_stats = defaultdict(lambda: {
#             'admissions': 0,
#             'stay_days': [],
#             'diagnoses': defaultdict(int),
#             'readmissions': 0
#         })
        
#         for visit in visits_data:
#             department = visit[0]
#             diagnosis = visit[1]
#             admission = visit[2]
#             discharge = visit[3]
            
#             dept_stats[department]['admissions'] += 1
            
#             if admission and discharge:
#                 stay = calculate_avg_stay(admission, discharge)
#                 dept_stats[department]['stay_days'].append(stay)
            
#             if diagnosis:
#                 dept_stats[department]['diagnoses'][diagnosis] += 1
        
#         for flag in readmissions_data:
#             department = flag[0]
#             dept_stats[department]['readmissions'] += 1
        
#         metrics = []
#         reporting_period = datetime.now().strftime('%Y-%m')
        
#         context.log.info(f"📊 Computing KPIs for {len(dept_stats)} departments...")
        
#         for department, stats in dept_stats.items():
#             total_admissions = stats['admissions']
#             readmission_count = stats['readmissions']
            
#             if stats['stay_days']:
#                 avg_stay = sum(stats['stay_days']) / len(stats['stay_days'])
#             else:
#                 avg_stay = 0.0
            
#             if total_admissions > 0:
#                 readmission_rate = readmission_count / total_admissions
#             else:
#                 readmission_rate = 0.0
            
#             if stats['diagnoses']:
#                 top_diagnosis = max(stats['diagnoses'], key=stats['diagnoses'].get)
#             else:
#                 top_diagnosis = None
            
#             metrics.append({
#                 'department': department,
#                 'reporting_period': reporting_period,
#                 'total_admissions': total_admissions,
#                 'avg_stay_days': round(avg_stay, 2),
#                 'readmission_count': readmission_count,
#                 'readmission_rate': round(readmission_rate, 4),
#                 'top_diagnosis_code': top_diagnosis,
#                 'bed_utilization_rate': 0.75
#             })
        
#         if metrics:
#             count = postgres.load_rows(metrics, "department_metrics")
#             context.log.info(f"✅ Created metrics for {count} departments")
            
#             # Display department performance summary
#             context.log.info(f"📊 Department Performance Summary (Period: {reporting_period}):")
#             for metric in sorted(metrics, key=lambda x: x['readmission_rate'], reverse=True)[:5]:
#                 context.log.info(f"   └─ {metric['department']}:")
#                 context.log.info(f"      ├─ Admissions: {metric['total_admissions']}")
#                 context.log.info(f"      ├─ Avg Stay: {metric['avg_stay_days']} days")
#                 context.log.info(f"      ├─ Readmission Rate: {metric['readmission_rate']*100:.1f}%")
#                 context.log.info(f"      └─ Top Diagnosis: {metric['top_diagnosis_code'] or 'N/A'}")
#         else:
#             count = 0
#             context.log.warning("⚠️  No department metrics generated")
        
#         return dg.MaterializeResult(metadata={"department_count": count})
#     except Exception as e:
#         context.log.error(f"❌ Error creating department metrics: {str(e)}")
#         raise



"""Dagster assets for the Charite Clinical Analytics Pipeline.

All data is synthetic/fictional. No real PHI is used.
"""

import pandas as pd
from datetime import datetime, date
from pathlib import Path
from collections import defaultdict
from typing import Any
import os

import dagster as dg

from clinicflow.defs.resources import PostgresResource

DATA_DIR = Path(__file__).resolve().parents[4] / "data"
S3_BUCKET = os.getenv("CLINICFLOW_S3_BUCKET", "")


def read_csv_from_s3(key: str) -> pd.DataFrame:
    """Read a CSV file from S3 and return a pandas DataFrame."""
    try:
        import boto3
        import io
        
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = response["Body"].read().decode("utf-8")
        return pd.read_csv(io.StringIO(content))
    except ImportError:
        raise ImportError("boto3 is required for S3 access. Install with: uv add boto3")
    except Exception as e:
        raise Exception(f"Error reading from S3: {str(e)}")


def read_csv_local(file_path: Path) -> pd.DataFrame:
    """Read a CSV file from local filesystem."""
    return pd.read_csv(file_path)


def read_csv_data(file_name: str) -> pd.DataFrame:
    """Read CSV data from either S3 or local filesystem based on environment."""
    if S3_BUCKET:
        return read_csv_from_s3(f"data/{file_name}")
    else:
        return read_csv_local(DATA_DIR / file_name)


def detect_readmissions(
    visits,
    window_days: int = 30,
) -> list[dict]:
    """Detect readmissions within a configurable window.
    
    Works with both list of dicts and pandas DataFrame.
    """
    flags = []
    
    try:
        if isinstance(visits, list):
            visits_df = pd.DataFrame(visits)
        else:
            visits_df = visits.copy()
        
        visits_df['admission_date'] = pd.to_datetime(visits_df['admission_date'])
        visits_df['discharge_date'] = pd.to_datetime(visits_df['discharge_date'])
        
        sorted_visits = visits_df.sort_values(['patient_id', 'admission_date'])
        
        for patient_id, group in sorted_visits.groupby('patient_id'):
            group_list = group.to_dict('records')
            
            for i in range(len(group_list) - 1):
                current = group_list[i]
                next_visit = group_list[i + 1]
                
                if current['patient_id'] == next_visit['patient_id']:
                    discharge = current['discharge_date']
                    admission = next_visit['admission_date']
                    
                    if pd.notna(discharge) and pd.notna(admission):
                        days_between = (admission - discharge).days
                        
                        if days_between <= window_days:
                            flags.append({
                                'patient_id': patient_id,
                                'original_visit_id': current['visit_id'],
                                'readmission_visit_id': next_visit['visit_id'],
                                'days_between': days_between,
                                'department': next_visit.get('department', 'Unknown')
                            })
    except Exception as e:
        raise Exception(f"Error detecting readmissions: {str(e)}")
    
    return flags


def calculate_avg_stay(
    admission_date: datetime,
    discharge_date: datetime,
) -> float:
    """Calculate length of stay in days."""
    try:
        if pd.isna(discharge_date) or discharge_date < admission_date:
            return 0.0
        
        if isinstance(admission_date, str):
            admission = pd.to_datetime(admission_date)
        else:
            admission = admission_date
            
        if isinstance(discharge_date, str):
            discharge = pd.to_datetime(discharge_date)
        else:
            discharge = discharge_date
        
        return float((discharge - admission).days)
    except Exception as e:
        raise Exception(f"Error calculating average stay: {str(e)}")


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "pandas", "postgres"},
)
def raw_patients(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load patients.csv into the patients table using pandas."""
    try:
        context.log.info("📂 Reading patients.csv...")
        df = read_csv_data("patients.csv")
        
        context.log.info(f"✅ Loaded {len(df)} patient records from CSV")
        
        context.log.info("🔍 Validating data quality...")
        missing_values = df.isnull().sum()
        if missing_values.any():
            context.log.warning(f"⚠️  Missing values detected:\n{missing_values[missing_values > 0]}")
        
        count = postgres.load_dataframe(df, "patients")
        
        context.log.info(f"💾 Successfully inserted {count} patients into database")
        context.log.info(f"📊 Patient Data Summary:")
        context.log.info(f"   └─ Total patients: {count}")
        context.log.info(f"   └─ Gender distribution: {df['gender'].value_counts().to_dict()}")
        context.log.info(f"   └─ Blood type distribution: {df['blood_type'].value_counts().to_dict()}")
        
        return dg.MaterializeResult(metadata={"row_count": count})
    except Exception as e:
        context.log.error(f"❌ Error loading patients: {str(e)}")
        raise


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "pandas", "postgres"},
    deps=[raw_patients],
)
def raw_visits(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load visits.csv into the visits table using pandas."""
    try:
        context.log.info("📂 Reading visits.csv...")
        df = read_csv_data("visits.csv")
        
        context.log.info(f"✅ Loaded {len(df)} visit records from CSV")
        
        df['admission_date'] = pd.to_datetime(df['admission_date'])
        df['discharge_date'] = pd.to_datetime(df['discharge_date'])
        
        count = postgres.load_dataframe(df, "visits")
        
        context.log.info(f"💾 Successfully inserted {count} visits into database")
        context.log.info(f"📊 Visit Data Summary:")
        context.log.info(f"   └─ Total visits: {count}")
        context.log.info(f"   └─ Department distribution: {df['department'].value_counts().to_dict()}")
        context.log.info(f"   └─ Date range: {df['admission_date'].min().date()} to {df['admission_date'].max().date()}")
        
        return dg.MaterializeResult(metadata={"row_count": count})
    except Exception as e:
        context.log.error(f"❌ Error loading visits: {str(e)}")
        raise


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "pandas", "postgres"},
)
def raw_diagnoses(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load diagnoses.csv into the diagnoses table using pandas."""
    try:
        context.log.info("📂 Reading diagnoses.csv...")
        df = read_csv_data("diagnoses.csv")
        
        context.log.info(f"✅ Loaded {len(df)} diagnosis records from CSV")
        
        count = postgres.load_dataframe(df, "diagnoses")
        
        context.log.info(f"💾 Successfully inserted {count} diagnoses into database")
        context.log.info(f"📊 Diagnosis Data Summary:")
        context.log.info(f"   └─ Total diagnoses: {count}")
        context.log.info(f"   └─ Category distribution: {df['category'].value_counts().to_dict()}")
        context.log.info(f"   └─ Severity distribution: {df['severity_level'].value_counts().sort_index().to_dict()}")
        
        return dg.MaterializeResult(metadata={"row_count": count})
    except Exception as e:
        context.log.error(f"❌ Error loading diagnoses: {str(e)}")
        raise


@dg.asset(
    group_name="raw_ingestion",
    kinds={"python", "pandas", "postgres"},
    deps=[raw_visits],
)
def raw_prescriptions(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Load prescriptions.csv into the prescriptions table using pandas."""
    try:
        context.log.info("📂 Reading prescriptions.csv...")
        df = read_csv_data("prescriptions.csv")
        
        context.log.info(f"✅ Loaded {len(df)} prescription records from CSV")
        
        df['end_date'] = df['end_date'].replace('', None)
        df['start_date'] = pd.to_datetime(df['start_date'])
        if 'end_date' in df.columns:
            df['end_date'] = pd.to_datetime(df['end_date'])
        
        empty_end_date_count = df['end_date'].isna().sum() if 'end_date' in df.columns else 0
        if empty_end_date_count > 0:
            context.log.info(f"🔄 Converted {empty_end_date_count} empty end_date fields to NULL")
        
        visits_df = postgres.execute_query("SELECT visit_id FROM visits")
        existing_visit_ids = {row[0] for row in visits_df}
        
        valid_mask = df['visit_id'].isin(existing_visit_ids)
        valid_df = df[valid_mask]
        
        if len(valid_df) < len(df):
            missing_count = len(df) - len(valid_df)
            context.log.warning(f"⚠️  Skipping {missing_count} prescriptions with missing visit references")
        
        if not valid_df.empty:
            count = postgres.load_dataframe(valid_df, "prescriptions")
            context.log.info(f"💾 Successfully inserted {count} prescriptions into database")
            
            context.log.info(f"📊 Prescription Data Summary:")
            context.log.info(f"   └─ Total prescriptions loaded: {count}")
            context.log.info(f"   └─ Active prescriptions (no end date): {valid_df['end_date'].isna().sum()}")
            context.log.info(f"   └─ Top 3 medications: {valid_df['medication_name'].value_counts().head(3).to_dict()}")
        else:
            count = 0
            context.log.warning("⚠️  No valid prescriptions to load")
        
        return dg.MaterializeResult(metadata={"row_count": count})
    except Exception as e:
        context.log.error(f"❌ Error loading prescriptions: {str(e)}")
        raise


@dg.asset(
    deps=[raw_visits],
    group_name="analytics",
    kinds={"python", "pandas", "postgres"},
)
def readmission_flags(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Flag patients readmitted within a configurable window using pandas."""
    try:
        context.log.info("🔍 Analyzing visits for readmission patterns...")
        
        visits_data = postgres.execute_query(
            "SELECT visit_id, patient_id, department, admission_date, "
            "discharge_date FROM visits WHERE status = 'completed' "
            "ORDER BY patient_id, admission_date"
        )
        
        visits_df = pd.DataFrame(visits_data, columns=[
            'visit_id', 'patient_id', 'department', 'admission_date', 'discharge_date'
        ])
        
        context.log.info(f"📊 Retrieved {len(visits_df)} completed visits from database")
        
        flags = detect_readmissions(visits_df, window_days=30)
        
        if flags:
            flag_count = postgres.load_rows(flags, "readmission_flags")
            context.log.info(f"🏥 Detected {flag_count} readmission cases")
            
            flags_df = pd.DataFrame(flags)
            dept_counts = flags_df['department'].value_counts()
            
            context.log.info(f"📊 Readmission Analysis:")
            context.log.info(f"   └─ Total readmissions: {flag_count}")
            context.log.info(f"   └─ Departments with most readmissions: {dept_counts.head(3).to_dict()}")
            
            avg_days = flags_df['days_between'].mean()
            context.log.info(f"   └─ Average days between readmissions: {avg_days:.1f} days")
        else:
            flag_count = 0
            context.log.info("✅ No readmissions detected within the 30-day window")
        
        return dg.MaterializeResult(metadata={"flag_count": flag_count})
    except Exception as e:
        context.log.error(f"❌ Error detecting readmission flags: {str(e)}")
        raise


@dg.asset(
    deps=[raw_patients, raw_visits, raw_prescriptions],
    group_name="analytics",
    kinds={"python", "pandas", "postgres"},
)
def patient_summaries(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Aggregate per-patient statistics using pandas."""
    try:
        context.log.info("📊 Generating patient summary analytics...")
        
        patients_df = pd.DataFrame(
            postgres.execute_query("SELECT patient_id FROM patients"),
            columns=['patient_id']
        )
        context.log.info(f"👥 Processing {len(patients_df)} patients")
        
        visits_df = pd.DataFrame(
            postgres.execute_query(
                "SELECT patient_id, department, admission_date, discharge_date "
                "FROM visits WHERE status = 'completed'"
            ),
            columns=['patient_id', 'department', 'admission_date', 'discharge_date']
        )
        context.log.info(f"📋 Retrieved {len(visits_df)} visit records")
        
        prescriptions_data = postgres.execute_query("SELECT patient_id, end_date FROM prescriptions")
        if prescriptions_data:
            prescriptions_df = pd.DataFrame(prescriptions_data, columns=['patient_id', 'end_date'])
        else:
            prescriptions_df = pd.DataFrame(columns=['patient_id', 'end_date'])
        context.log.info(f"💊 Retrieved {len(prescriptions_df)} prescription records")
        
        readmissions_data = postgres.execute_query("SELECT patient_id FROM readmission_flags")
        if readmissions_data:
            readmissions_df = pd.DataFrame(readmissions_data, columns=['patient_id'])
            readmission_patients = set(readmissions_df['patient_id'].tolist())
            context.log.info(f"⚠️  {len(readmission_patients)} patients have readmission flags")
        else:
            readmission_patients = set()
        
        if visits_df.empty:
            context.log.warning("⚠️  No visits found, creating empty summaries")
            count = 0
            return dg.MaterializeResult(metadata={"patient_count": count})
        
        if visits_df['admission_date'].dtype == 'object':
            visits_df['admission_date'] = pd.to_datetime(visits_df['admission_date'])
        if visits_df['discharge_date'].dtype == 'object':
            visits_df['discharge_date'] = pd.to_datetime(visits_df['discharge_date'])
        
        visits_df['stay_days'] = (visits_df['discharge_date'] - visits_df['admission_date']).dt.days.fillna(0)
        
        total_visits = visits_df.groupby('patient_id').size().reset_index(name='total_visits')
        
        last_visit = visits_df.groupby('patient_id')['admission_date'].max().reset_index(name='last_visit_date')
        
        avg_stay = visits_df.groupby('patient_id')['stay_days'].mean().reset_index(name='avg_stay_days')
        
        def get_primary_department(group):
            if len(group) > 0:
                return group.mode().iloc[0] if not group.mode().empty else None
            return None
        
        primary_dept = visits_df.groupby('patient_id')['department'].agg(get_primary_department).reset_index(name='primary_department')
        
        visit_stats = total_visits.merge(last_visit, on='patient_id', how='left')
        visit_stats = visit_stats.merge(avg_stay, on='patient_id', how='left')
        visit_stats = visit_stats.merge(primary_dept, on='patient_id', how='left')
        
        today = datetime.now().date()
        
        def is_active(end_date):
            if pd.isna(end_date):
                return True
            if isinstance(end_date, pd.Timestamp):
                end_date = end_date.date()
            return end_date > today
        
        if not prescriptions_df.empty:
            prescriptions_df['is_active'] = prescriptions_df['end_date'].apply(is_active)
            active_prescriptions = prescriptions_df[prescriptions_df['is_active']].groupby('patient_id').size().reset_index(name='active_prescriptions')
        else:
            active_prescriptions = pd.DataFrame(columns=['patient_id', 'active_prescriptions'])
        
        summaries_df = patients_df.merge(visit_stats, on='patient_id', how='left')
        summaries_df = summaries_df.merge(active_prescriptions, on='patient_id', how='left')
        
        summaries_df['total_visits'] = summaries_df['total_visits'].fillna(0).astype(int)
        summaries_df['avg_stay_days'] = summaries_df['avg_stay_days'].fillna(0).round(2)
        summaries_df['active_prescriptions'] = summaries_df['active_prescriptions'].fillna(0).astype(int)
        
        summaries_df['risk_category'] = 'low'
        summaries_df.loc[summaries_df['total_visits'] >= 3, 'risk_category'] = 'medium'
        summaries_df.loc[(summaries_df['total_visits'] >= 5) | (summaries_df['patient_id'].isin(readmission_patients)), 'risk_category'] = 'high'
        
        risk_distribution = summaries_df['risk_category'].value_counts().to_dict()
        
        summaries = []
        for _, row in summaries_df.iterrows():
            last_visit_val = row['last_visit_date']
            if pd.notna(last_visit_val):
                if isinstance(last_visit_val, pd.Timestamp):
                    last_visit_val = last_visit_val.date()
            else:
                last_visit_val = None
            
            summary = {
                'patient_id': row['patient_id'],
                'total_visits': int(row['total_visits']),
                'last_visit_date': last_visit_val,
                'primary_department': row['primary_department'],
                'avg_stay_days': float(row['avg_stay_days']),
                'active_prescriptions': int(row['active_prescriptions']),
                'risk_category': row['risk_category']
            }
            summaries.append(summary)
        
        if summaries:
            count = postgres.load_rows(summaries, "patient_summaries")
            context.log.info(f"✅ Created {count} patient summaries")
            
            context.log.info(f"📊 Patient Risk Distribution:")
            context.log.info(f"   └─ High risk: {risk_distribution.get('high', 0)} patients")
            context.log.info(f"   └─ Medium risk: {risk_distribution.get('medium', 0)} patients")
            context.log.info(f"   └─ Low risk: {risk_distribution.get('low', 0)} patients")
            
            context.log.info(f"📈 Average Metrics:")
            context.log.info(f"   └─ Visits per patient: {summaries_df['total_visits'].mean():.1f}")
            context.log.info(f"   └─ Active prescriptions per patient: {summaries_df['active_prescriptions'].mean():.1f}")
        else:
            count = 0
            context.log.warning("⚠️  No patient summaries generated")
        
        return dg.MaterializeResult(metadata={"patient_count": count})
    except Exception as e:
        context.log.error(f"❌ Error creating patient summaries: {str(e)}")
        raise


@dg.asset(
    deps=[raw_visits, raw_diagnoses, readmission_flags],
    group_name="analytics",
    kinds={"python", "pandas", "postgres"},
)
def department_metrics(
    context: dg.AssetExecutionContext,
    postgres: PostgresResource,
) -> dg.MaterializeResult:
    """Calculate per-department performance KPIs using pandas."""
    try:
        context.log.info("🏥 Calculating department performance metrics...")
        
        visits_data = postgres.execute_query(
            "SELECT department, diagnosis_code, admission_date, discharge_date "
            "FROM visits WHERE status = 'completed'"
        )
        
        if not visits_data:
            context.log.warning("⚠️  No visits found, skipping department metrics")
            return dg.MaterializeResult(metadata={"department_count": 0})
        
        visits_df = pd.DataFrame(visits_data, columns=['department', 'diagnosis_code', 'admission_date', 'discharge_date'])
        context.log.info(f"📊 Retrieved {len(visits_df)} visits for analysis")
        
        readmissions_data = postgres.execute_query("SELECT department FROM readmission_flags")
        if readmissions_data:
            readmissions_df = pd.DataFrame(readmissions_data, columns=['department'])
        else:
            readmissions_df = pd.DataFrame(columns=['department'])
        context.log.info(f"🏥 Retrieved {len(readmissions_df)} readmission records")
        
        if visits_df['admission_date'].dtype == 'object':
            visits_df['admission_date'] = pd.to_datetime(visits_df['admission_date'])
        if visits_df['discharge_date'].dtype == 'object':
            visits_df['discharge_date'] = pd.to_datetime(visits_df['discharge_date'])
        
        visits_df['stay_days'] = (visits_df['discharge_date'] - visits_df['admission_date']).dt.days.fillna(0)
        
        dept_metrics = visits_df.groupby('department').agg({
            'admission_date': 'count',
            'stay_days': 'mean',
            'diagnosis_code': lambda x: x.mode().iloc[0] if not x.empty and not x.mode().empty else None
        }).reset_index()
        
        dept_metrics.columns = ['department', 'total_admissions', 'avg_stay_days', 'top_diagnosis_code']
        
        if not readmissions_df.empty:
            readmission_counts = readmissions_df['department'].value_counts().reset_index()
            readmission_counts.columns = ['department', 'readmission_count']
            dept_metrics = dept_metrics.merge(readmission_counts, on='department', how='left')
        dept_metrics['readmission_count'] = dept_metrics['readmission_count'].fillna(0).astype(int)
        
        dept_metrics['readmission_rate'] = dept_metrics['readmission_count'] / dept_metrics['total_admissions']
        dept_metrics['readmission_rate'] = dept_metrics['readmission_rate'].round(4)
        
        dept_metrics['reporting_period'] = datetime.now().strftime('%Y-%m')
        dept_metrics['bed_utilization_rate'] = 0.75
        
        metrics = dept_metrics.to_dict('records')
        
        if metrics:
            count = postgres.load_rows(metrics, "department_metrics")
            context.log.info(f"✅ Created metrics for {count} departments")
            
            context.log.info(f"📊 Department Performance Summary (Period: {dept_metrics['reporting_period'].iloc[0]}):")
            for _, metric in dept_metrics.sort_values('readmission_rate', ascending=False).head().iterrows():
                context.log.info(f"   └─ {metric['department']}:")
                context.log.info(f"      ├─ Admissions: {metric['total_admissions']}")
                context.log.info(f"      ├─ Avg Stay: {metric['avg_stay_days']:.1f} days")
                context.log.info(f"      ├─ Readmission Rate: {metric['readmission_rate']*100:.1f}%")
                context.log.info(f"      └─ Top Diagnosis: {metric['top_diagnosis_code'] or 'N/A'}")
        else:
            count = 0
            context.log.warning("⚠️  No department metrics generated")
        
        return dg.MaterializeResult(metadata={"department_count": count})
    except Exception as e:
        context.log.error(f"❌ Error creating department metrics: {str(e)}")
        raise