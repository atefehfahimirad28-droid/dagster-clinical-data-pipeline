# AWS Deployment Guide (Optional / Advanced)

This guide walks you through deploying the ClinicFlow pipeline to AWS.
It targets the **AWS Free Tier** wherever possible to keep costs minimal.

## Cost Estimate

| Service | Tier | Monthly Cost |
|---------|------|-------------|
| EC2 `t3.micro` | Free Tier (750 h/mo for 12 months) | $0.00 |
| RDS PostgreSQL `db.t3.micro` | Free Tier (750 h/mo for 12 months) | $0.00 |
| S3 (CSV storage) | Free Tier (5 GB) | $0.00 |
| **Total (Free Tier)** | | **$0.00** |
| **After Free Tier expires** | | **~$15-20/mo** |

> **Important:** Always set a billing alarm and tear down resources when done.

## Architecture

```
┌──────────┐       ┌──────────────────────────┐       ┌──────────────┐
│  S3      │       │  EC2 (t3.micro)          │       │  RDS         │
│  Bucket  │──────►│  Dagster + ClinicFlow     │──────►│  PostgreSQL  │
│  (CSVs)  │       │  (dagster-webserver +    │       │  (db.t3.micro│
│          │       │   dagster-daemon)        │       │  Free Tier)  │
└──────────┘       └──────────────────────────┘       └──────────────┘
```

## Prerequisites

- An AWS account (Free Tier eligible)
- AWS CLI installed and configured (`aws configure`)
- An SSH key pair created in your target region

## Step 1: Create an RDS PostgreSQL Instance

```bash
# Create a security group for the database
aws ec2 create-security-group \
  --group-name clinicflow-db-sg \
  --description "ClinicFlow PostgreSQL"

# Allow PostgreSQL traffic from your EC2 (we will refine this later)
aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-db-sg \
  --protocol tcp \
  --port 5432 \
  --source-group clinicflow-ec2-sg

# Create the RDS instance (Free Tier eligible)
aws rds create-db-instance \
  --db-instance-identifier clinicflow-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 17 \
  --master-username clinicflow \
  --master-user-password '<CHOOSE-A-STRONG-PASSWORD>' \
  --allocated-storage 20 \
  --no-multi-az \
  --no-publicly-accessible \
  --vpc-security-group-ids <sg-id-from-above> \
  --backup-retention-period 1 \
  --storage-type gp2

# Wait for the instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier clinicflow-db
```

Once available, note the **Endpoint** from:

```bash
aws rds describe-db-instances \
  --db-instance-identifier clinicflow-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### Initialize the Schema

Connect to RDS and run the init script:

```bash
psql "postgresql://clinicflow:<PASSWORD>@<RDS-ENDPOINT>:5432/postgres" \
  -c "CREATE DATABASE clinicflow;"

psql "postgresql://clinicflow:<PASSWORD>@<RDS-ENDPOINT>:5432/clinicflow" \
  -f db/init.sql
```

## Step 2: Create an S3 Bucket for CSV Data

```bash
aws s3 mb s3://clinicflow-data-<your-account-id> --region eu-central-1

# Upload the CSV files
aws s3 cp data/ s3://clinicflow-data-<your-account-id>/data/ --recursive
```

## Step 3: Launch an EC2 Instance

```bash
# Create a security group for the EC2 instance
aws ec2 create-security-group \
  --group-name clinicflow-ec2-sg \
  --description "ClinicFlow EC2"

# Allow SSH and Dagit UI access
aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-ec2-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name clinicflow-ec2-sg \
  --protocol tcp --port 3000 --cidr 0.0.0.0/0

# Launch a t3.micro instance (Free Tier)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name <your-key-pair> \
  --security-groups clinicflow-ec2-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=clinicflow}]' \
  --count 1
```

> **Note:** The AMI ID above is an example (Amazon Linux 2). Find the latest
> for your region at the [EC2 console](https://console.aws.amazon.com/ec2/).

## Step 4: Set Up the EC2 Instance

SSH into the instance and install dependencies:

```bash
ssh -i <your-key>.pem ec2-user@<EC2-PUBLIC-IP>

# Install Python 3.12+ and uv
sudo yum update -y
sudo yum install -y python3.12 git
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Clone the project
git clone <your-repo-url> clinicflow-project
cd clinicflow-project/clinicflow

# Install dependencies
uv sync --dev
```

## Step 5: Configure Environment Variables

Create a `.env` file (do **not** commit this):

```bash
cat > .env << 'EOF'
CLINICFLOW_DB_HOST=<RDS-ENDPOINT>
CLINICFLOW_DB_PORT=5432
CLINICFLOW_DB_NAME=clinicflow
CLINICFLOW_DB_USER=clinicflow
CLINICFLOW_DB_PASSWORD=<YOUR-RDS-PASSWORD>
CLINICFLOW_S3_BUCKET=clinicflow-data-<your-account-id>
EOF
```

> **Tip:** For production, use AWS Secrets Manager or SSM Parameter Store
> instead of `.env` files.

## Step 6: Run Dagster

```bash
# Start the Dagster webserver and daemon
DAGSTER_HOME=~/dagster_home dg dev --host 0.0.0.0 --port 3000
```

Access Dagit at `http://<EC2-PUBLIC-IP>:3000`.

## Step 7: Tear Down (Important!)

When you are done, destroy all resources to avoid charges:

```bash
# Terminate EC2
aws ec2 terminate-instances --instance-ids <instance-id>

# Delete RDS
aws rds delete-db-instance \
  --db-instance-identifier clinicflow-db \
  --skip-final-snapshot

# Empty and delete S3 bucket
aws s3 rm s3://clinicflow-data-<your-account-id> --recursive
aws s3 rb s3://clinicflow-data-<your-account-id>

# Delete security groups (after instances are terminated)
aws ec2 delete-security-group --group-name clinicflow-ec2-sg
aws ec2 delete-security-group --group-name clinicflow-db-sg
```

## Adapting the Code for AWS

To read CSVs from S3 instead of the local `data/` directory, you can add
a small helper using `boto3`:

```python
import boto3
import csv
import io
import os

def read_csv_from_s3(key: str) -> list[dict]:
    """Read a CSV file from S3 and return a list of dicts."""
    s3 = boto3.client("s3")
    bucket = os.environ["CLINICFLOW_S3_BUCKET"]
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)
```

Add `boto3` to your dependencies:

```bash
uv add boto3
```

## Tips for Staying on Free Tier

1. **Stop the EC2 instance** when not in use (you only pay for running hours)
2. **Use `db.t3.micro`** for RDS -- it is Free Tier eligible
3. **Set a billing alarm** at $5 in CloudWatch to get notified early
4. **Delete everything** when the project is complete
5. **Use one region** (e.g., `eu-central-1`) to avoid cross-region charges
