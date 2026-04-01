# ADR-002: Data Privacy Considerations for Clinical Data

**Status:** Accepted
**Date:** 2026-04-01

## Context

The Charite Clinical Analytics Pipeline processes clinical data including patient
demographics, visit records, diagnoses, and prescriptions. Although all data in
this project is **synthetic and fictional**, the pipeline architecture must be
designed with awareness of the privacy requirements that would apply to real
Protected Health Information (PHI).

Clinical data is among the most sensitive categories of personal data under both
European and international privacy frameworks:

- **GDPR Article 9** classifies health data as a "special category" of personal
  data, requiring explicit consent or a specific legal basis for processing.
- **HIPAA** (U.S.) defines 18 types of Protected Health Information and mandates
  administrative, physical, and technical safeguards.
- **German BDSG** (Bundesdatenschutzgesetz) provides additional national-level
  requirements on top of the GDPR.

Even in an educational setting, it is important to establish the right patterns
so that the architecture could be adapted for production use with real PHI.

## Decision

We design a privacy-aware architecture from the start, even though the current
data is synthetic. The project implements baseline protections and documents what
additional measures would be required for production deployment with real PHI.

### Current project safeguards

1. **No real PHI.** All patient data is generated synthetically. Names, dates of
   birth, and clinical details are entirely fictional.
2. **Credentials in environment variables.** The PostgreSQL connection string uses
   a default development credential (`clinicflow:clinicflow`). In a real deployment,
   credentials would be stored in a secrets manager (e.g., HashiCorp Vault, AWS
   Secrets Manager) and injected via environment variables or Dagster's
   `EnvVar` configuration.
3. **Docker network isolation.** PostgreSQL runs in a Docker container with port
   mapping restricted to localhost (`5432:5432`), preventing external network access
   during development.
4. **`.gitignore` hygiene.** Environment files (`.env`) containing credentials are
   excluded from version control.

### What would be needed for production with real PHI

#### Access control

- **Role-based access control (RBAC) in PostgreSQL.** Define granular roles
  (e.g., `pipeline_writer`, `analyst_reader`, `admin`) with least-privilege
  permissions on each table. Analysts should not have write access to raw tables;
  the pipeline service account should not have access to audit tables.
- **Row-level security (RLS).** PostgreSQL supports RLS policies to restrict which
  rows a user can see based on their role, useful for multi-department access.
- **Application-level authorization.** The Dagster webserver should require
  authentication (e.g., SSO/OIDC) and role-based access to asset materialization.

#### Encryption

- **At rest.** Enable PostgreSQL's Transparent Data Encryption (TDE) or use
  encrypted storage volumes. Consider column-level encryption for highly sensitive
  fields (e.g., `date_of_birth`, `first_name`, `last_name`) using `pgcrypto`.
- **In transit.** Enforce TLS for all PostgreSQL connections (`sslmode=require`
  or `sslmode=verify-full` in the connection string).

#### Anonymization and pseudonymization

- **k-anonymity.** Ensure that any published analytics dataset cannot identify
  an individual by combining quasi-identifiers (age, gender, department). Generalize
  or suppress values until each combination maps to at least *k* individuals.
- **Differential privacy.** For aggregate statistics (e.g., `department_metrics`),
  consider adding calibrated noise to prevent inference attacks on small groups.
- **Pseudonymization.** Replace direct identifiers (`patient_id`, names) with
  pseudonyms in analytics tables. Maintain the mapping in a separate, restricted
  keystore.

#### Audit logging

- **Audit tables.** Log every data access and modification: who accessed what data,
  when, and from which application. PostgreSQL's `pgaudit` extension provides
  statement-level and object-level audit logging.
- **Pipeline run logs.** Dagster already records run metadata; in production, these
  logs should be forwarded to a centralized, tamper-evident logging system (e.g.,
  SIEM).

#### Data minimization and retention

- **Data minimization principle (GDPR Article 5(1)(c)).** Collect and store only
  the data elements strictly necessary for the analytics purpose. Review each
  column in the schema and justify its inclusion.
- **Retention policies.** Define how long each category of data is retained.
  Implement automated deletion or archival jobs (e.g., a Dagster scheduled job)
  that enforce these policies.
- **Right to erasure (GDPR Article 17).** Support deletion of all data related
  to a specific patient. The foreign key constraints with `CASCADE` in our schema
  facilitate this, but computed tables (`patient_summaries`, `readmission_flags`)
  must also be recomputed after erasure.

## Consequences

### Positive

- **Production-ready patterns.** Even though data is synthetic, the architecture
  follows conventions (resource injection, credential externalization, Docker
  isolation) that transfer directly to production deployments.
- **Educational value.** Junior data engineers learn to think about privacy from
  the design phase, not as an afterthought.
- **Regulatory awareness.** Documenting GDPR, HIPAA, and BDSG requirements builds
  the team's understanding of the compliance landscape for health data.

### Negative

- **Overhead for a learning project.** Some of the documented production measures
  (column-level encryption, RLS, pgaudit) are not implemented in this project,
  which could create a gap between documented intent and actual state.
- **Complexity for beginners.** Privacy engineering introduces concepts (k-anonymity,
  differential privacy) that may be unfamiliar to junior engineers and require
  additional study.
