"""passport.py — assemble enriched items into full passport records.

A "record" is a dict keyed by the template header names in config.COLUMN_MAP
(e.g. record["Description"], record["Volume (m3)"]). This is the single shape
consumed by fill_excel, export_json, and visualize, so the mapping to columns
lives in exactly one place.

Public API
----------
build_record(item, index) -> dict     # one enriched item -> one passport record
build_records(items) -> list[dict]    # run parse->normalize->classify->carbon for all
"""
from __future__ import annotations


def build_record(item: dict, index: int) -> dict:
    """Map a fully-enriched item onto the template's header-keyed record."""
    raise NotImplementedError  # TODO: implement in the assembly step


def build_records(items: list[dict], with_carbon: bool = True) -> list[dict]:
    """Run the enrichment chain over raw items and return passport records."""
    raise NotImplementedError  # TODO: implement in the assembly step
