"""Dagster schedules for the Charite Clinical Analytics Pipeline.

Weekly schedule that triggers the full analytics pipeline every Monday morning.

German: Dagster-Zeitplaene fuer die klinische Analyse-Pipeline der Charite.

Woechentlicher Zeitplan, der die vollstaendige Analyse-Pipeline
jeden Montagmorgen ausloest.
"""

import dagster as dg

from clinicflow.defs.jobs import weekly_analytics_job

# ---------------------------------------------------------------------------
# Weekly analytics schedule
# DE: Woechentlicher Analyse-Zeitplan
# ---------------------------------------------------------------------------

weekly_analytics_schedule = dg.ScheduleDefinition(
    job=weekly_analytics_job,
    cron_schedule="0 7 * * 1",  # Every Monday at 07:00 / DE: Jeden Montag um 07:00
    default_status=dg.DefaultScheduleStatus.STOPPED,
    description="Runs the full clinical analytics pipeline every Monday at 07:00 AM.",
)
