"""Dagster definitions entry point for Charite Clinical Analytics Pipeline."""

from dagster import load_defs

import clinicflow.defs as defs_module

defs = load_defs(defs_module)
