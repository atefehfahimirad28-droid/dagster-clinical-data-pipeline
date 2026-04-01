# ADR-001: Orchestrator Choice -- Dagster

**Status:** Accepted
**Date:** 2026-04-01

## Context

The Charite Clinical Analytics Pipeline requires a data pipeline orchestrator to
coordinate CSV ingestion into PostgreSQL and downstream analytics computation.
The orchestrator must support:

- Defining data assets and their dependencies
- Managing database connections as shared resources
- Scheduling recurring pipeline runs
- Providing visibility into pipeline state and lineage
- Supporting a test-driven development workflow without requiring live infrastructure

The main candidates evaluated were **Dagster**, **Apache Airflow**, and **Prefect**.

## Decision

We chose **Dagster** as the pipeline orchestrator.

### Key reasons

1. **Asset-centric model (software-defined assets).**
   Dagster organizes pipelines around *assets* -- the data artifacts the pipeline
   produces -- rather than *tasks*. This maps naturally to our domain: we reason
   about `raw_patients`, `readmission_flags`, and `department_metrics` as first-class
   objects with declared dependencies. Airflow and Prefect are primarily task-centric,
   meaning the focus is on "what code runs" rather than "what data is produced."

2. **First-class resource management.**
   Dagster's `ConfigurableResource` system (used by our `PostgresResource`) provides
   dependency injection for external services. Resources are declared once and
   automatically provided to any asset that requests them. This avoids the global
   connection patterns common in Airflow (Connections/Hooks) and makes testing
   straightforward -- resources can be swapped with mocks or stubs.

3. **Native testing support without infrastructure.**
   Assets and helper functions can be tested as plain Python without spinning up
   a scheduler, database, or Docker container. Our 16 tests verify asset existence,
   dependency wiring, job definitions, and pure helper logic, all without a running
   PostgreSQL instance. Airflow's testing story typically requires a metadata database
   and more boilerplate.

4. **Built-in type system and metadata.**
   Assets return `MaterializeResult` with structured metadata (e.g., `row_count`,
   `flag_count`). This metadata is tracked across runs and surfaced in the Dagster UI,
   giving operators immediate insight into pipeline health.

5. **Modern Python-first API.**
   Dagster uses Python decorators (`@asset`, `@job`, `@schedule`) and type hints
   throughout. There is no need for YAML configuration files or external DSLs. This
   aligns well with our educational goal of teaching Python-native data engineering.

6. **Asset lineage visualization.**
   The Dagster UI (Dagit) renders the full asset dependency graph. For our pipeline,
   this means students and operators can visually trace the flow from `raw_visits`
   through `readmission_flags` to `department_metrics`, making the architecture
   immediately understandable.

## Consequences

### Positive

- **Testability.** Pure helper functions (`detect_readmissions`, `calculate_avg_stay`)
  and asset definitions can be tested independently, supporting TDD.
- **Asset lineage.** Dependencies between the 4 raw ingestion assets and 3 analytics
  assets are explicit and visualized automatically.
- **Resource injection.** `PostgresResource` is injected into assets automatically,
  enabling clean separation of concerns.
- **Idempotency.** The asset model encourages idempotent materializations --
  our assets use TRUNCATE + INSERT to ensure repeatable results.

### Negative

- **Smaller community than Airflow.** Airflow has a larger ecosystem of pre-built
  operators, providers, and community resources. Finding answers to niche Dagster
  questions may require consulting the official documentation or Dagster Slack.
- **Steeper learning curve for task-based thinkers.** Engineers accustomed to
  Airflow's DAG-of-tasks model need to shift their mental model to think in terms
  of assets and materializations rather than task execution order.
- **Fewer managed deployment options.** While Dagster Cloud exists, the range of
  managed hosting options is narrower than Airflow's (e.g., MWAA, Cloud Composer,
  Astronomer).
