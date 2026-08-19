"""carbon.py — BONUS B2: embodied-carbon enrichment (AMBER columns X, Y, Z).

Fills, only where a defensible factor exists:
  * Density (kg/m3)               -> column X
  * Embodied Carbon A1-A3 (kgCO2e)-> column Y
  * GWP / kg (kgCO2e/kg)          -> column Z

Factors and their citations live in data/reference/carbon_factors.csv (ICE
database, GreenPro, or peer-reviewed Indian LCA papers). The source string is
echoed into the Comment column so every carbon figure is traceable — as the
Instructions sheet requires for AMBER fields.

Carbon math
-----------
  mass_kg      = Weight column, or Volume(m3) * Density(kg/m3)
  A1A3 kgCO2e  = mass_kg * GWP_per_kg
Earth/labour-only items are tagged [EXCLUDED] with carbon 0 (see example row 4).

Public API
----------
load_factors(path) -> dict
enrich_carbon(item, factors) -> dict
"""
from __future__ import annotations

from pathlib import Path

from . import config


def load_factors(path: Path = config.CARBON_FACTORS_CSV) -> dict:
    """Load material -> {density, gwp_per_kg, source} from the reference CSV."""
    raise NotImplementedError  # TODO: implement in the carbon step


def enrich_carbon(item: dict, factors: dict | None = None) -> dict:
    """Populate Density / Embodied Carbon A1-A3 / GWP-per-kg where defensible."""
    raise NotImplementedError  # TODO: implement in the carbon step
