"""Dagster definitions entry point for Charite Clinical Analytics Pipeline.

German: Dagster-Definitionen als Einstiegspunkt fuer die klinische
Analyse-Pipeline der Charite.
"""

import dagster as dg

defs = dg.Definitions.merge(
    *dg.load_defs_from_package(
        "clinicflow.defs",
    ),
)
