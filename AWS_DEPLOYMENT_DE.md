# AWS-Bereitstellungsanleitung (Optional / Fortgeschritten)

Diese Anleitung fuehrt Sie durch die Bereitstellung der ClinicFlow-Pipeline auf AWS.
Sie nutzt wo immer moeglich das **AWS Free Tier**, um die Kosten minimal zu halten.

## Kostenschaetzung

| Dienst | Stufe | Monatliche Kosten |
|--------|-------|-------------------|
| EC2 `t3.micro` | Free Tier (750 h/Monat fuer 12 Monate) | 0,00 $ |
| RDS PostgreSQL `db.t3.micro` | Free Tier (750 h/Monat fuer 12 Monate) | 0,00 $ |
| S3 (CSV-Speicher) | Free Tier (5 GB) | 0,00 $ |
| **Gesamt (Free Tier)** | | **0,00 $** |
| **Nach Ablauf des Free Tier** | | **~15-20 $/Monat** |

> **Wichtig:** Richten Sie immer einen Abrechnungsalarm ein und entfernen Sie
> alle Ressourcen, wenn Sie fertig sind.

## Architektur

```
┌──────────┐       ┌──────────────────────────┐       ┌──────────────┐
│  S3      │       │  EC2 (t3.micro)          │       │  RDS         │
│  Bucket  │──────►│  Dagster + ClinicFlow     │──────►│  PostgreSQL  │
│  (CSVs)  │       │  (dagster-webserver +    │       │  (db.t3.micro│
│          │       │   dagster-daemon)        │       │  Free Tier)  │
└──────────┘       └──────────────────────────┘       └──────────────┘
```

## Voraussetzungen

- Ein AWS-Konto (Free-Tier-berechtigt)
- AWS CLI installiert und konfiguriert (`aws configure`)
- Ein SSH-Schluesselpaar in der Zielregion erstellt

## Schritt 1: RDS-PostgreSQL-Instanz erstellen

```bash
# Sicherheitsgruppe fuer die Datenbank erstellen
aws ec2 create-security-group \
  --group-name clinicflow-db-sg \
  --description "ClinicFlow PostgreSQL"

# PostgreSQL-Verkehr von EC2 erlauben
aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-db-sg \
  --protocol tcp \
  --port 5432 \
  --source-group clinicflow-ec2-sg

# RDS-Instanz erstellen (Free-Tier-berechtigt)
aws rds create-db-instance \
  --db-instance-identifier clinicflow-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 17 \
  --master-username clinicflow \
  --master-user-password '<SICHERES-PASSWORT-WAEHLEN>' \
  --allocated-storage 20 \
  --no-multi-az \
  --no-publicly-accessible \
  --vpc-security-group-ids <sg-id-von-oben> \
  --backup-retention-period 1 \
  --storage-type gp2

# Warten, bis die Instanz verfuegbar ist
aws rds wait db-instance-available \
  --db-instance-identifier clinicflow-db
```

Notieren Sie den **Endpunkt**:

```bash
aws rds describe-db-instances \
  --db-instance-identifier clinicflow-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### Schema initialisieren

Verbinden Sie sich mit RDS und fuehren Sie das Init-Skript aus:

```bash
psql "postgresql://clinicflow:<PASSWORT>@<RDS-ENDPUNKT>:5432/postgres" \
  -c "CREATE DATABASE clinicflow;"

psql "postgresql://clinicflow:<PASSWORT>@<RDS-ENDPUNKT>:5432/clinicflow" \
  -f db/init.sql
```

## Schritt 2: S3-Bucket fuer CSV-Daten erstellen

```bash
aws s3 mb s3://clinicflow-data-<ihre-konto-id> --region eu-central-1

# CSV-Dateien hochladen
aws s3 cp data/ s3://clinicflow-data-<ihre-konto-id>/data/ --recursive
```

## Schritt 3: EC2-Instanz starten

```bash
# Sicherheitsgruppe fuer die EC2-Instanz erstellen
aws ec2 create-security-group \
  --group-name clinicflow-ec2-sg \
  --description "ClinicFlow EC2"

# SSH- und Dagster-Benutzeroberflaeche-Zugriff erlauben
aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-ec2-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-ec2-sg \
  --protocol tcp --port 3000 --cidr 0.0.0.0/0

# t3.micro-Instanz starten (Free Tier)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name <ihr-schluesselpaar> \
  --security-groups clinicflow-ec2-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=clinicflow}]' \
  --count 1
```

> **Hinweis:** Die AMI-ID oben ist ein Beispiel (Amazon Linux 2). Die aktuelle
> finden Sie in der [EC2-Konsole](https://console.aws.amazon.com/ec2/).

## Schritt 4: EC2-Instanz einrichten

Per SSH verbinden und Abhaengigkeiten installieren:

```bash
ssh -i <ihr-schluessel>.pem ec2-user@<EC2-OEFFENTLICHE-IP>

# Python 3.12+ und uv installieren
sudo yum update -y
sudo yum install -y python3.12 git
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Projekt klonen
git clone <ihre-repo-url> clinicflow-project
cd clinicflow-project/clinicflow

# Abhaengigkeiten installieren
uv sync
```

## Schritt 5: Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env`-Datei (diese **nicht** committen):

```bash
cat > .env << 'EOF'
CLINICFLOW_DB_HOST=<RDS-ENDPUNKT>
CLINICFLOW_DB_PORT=5432
CLINICFLOW_DB_NAME=clinicflow
CLINICFLOW_DB_USER=clinicflow
CLINICFLOW_DB_PASSWORD=<IHR-RDS-PASSWORT>
CLINICFLOW_S3_BUCKET=clinicflow-data-<ihre-konto-id>
EOF
```

> **Tipp:** Fuer Produktionsumgebungen verwenden Sie AWS Secrets Manager oder
> SSM Parameter Store anstelle von `.env`-Dateien.

## Schritt 6: Dagster starten

```bash
# Dagster-Webserver und Daemon starten
DAGSTER_HOME=~/dagster_home dg dev --host 0.0.0.0 --port 3000
```

Dagster User Interface aufrufen unter `http://<EC2-OEFFENTLICHE-IP>:3000`.

## Schritt 7: Aufraumen (Wichtig!)

Wenn Sie fertig sind, alle Ressourcen entfernen, um Kosten zu vermeiden:

```bash
# EC2 beenden
aws ec2 terminate-instances --instance-ids <instanz-id>

# RDS loeschen
aws rds delete-db-instance \
  --db-instance-identifier clinicflow-db \
  --skip-final-snapshot

# S3-Bucket leeren und loeschen
aws s3 rm s3://clinicflow-data-<ihre-konto-id> --recursive
aws s3 rb s3://clinicflow-data-<ihre-konto-id>

# Sicherheitsgruppen loeschen (nach Beendigung der Instanzen)
aws ec2 delete-security-group --group-name clinicflow-ec2-sg
aws ec2 delete-security-group --group-name clinicflow-db-sg
```

## Code fuer AWS anpassen

Um CSVs aus S3 statt aus dem lokalen `data/`-Verzeichnis zu lesen,
koennen Sie einen kleinen Helfer mit `boto3` schreiben:

```python
import boto3
import csv
import io
import os

def read_csv_from_s3(key: str) -> list[dict]:
    """CSV-Datei aus S3 lesen und als Liste von Dicts zurueckgeben."""
    s3 = boto3.client("s3")
    bucket = os.environ["CLINICFLOW_S3_BUCKET"]
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)
```

`boto3` zu den Abhaengigkeiten hinzufuegen:

```bash
uv add boto3
```

## Tipps zum Einhalten des Free Tier

1. **EC2-Instanz stoppen**, wenn nicht in Benutzung (nur laufende Stunden kosten)
2. **`db.t3.micro` verwenden** fuer RDS -- ist Free-Tier-berechtigt
3. **Abrechnungsalarm bei 5 $** in CloudWatch einrichten
4. **Alles loeschen**, wenn das Projekt abgeschlossen ist
5. **Eine Region verwenden** (z. B. `eu-central-1`), um regionsuebergreifende Kosten zu vermeiden
