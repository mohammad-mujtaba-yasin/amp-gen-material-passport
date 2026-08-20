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

import csv
from pathlib import Path
from typing import Any

from . import config


def load_factors(path: Path = config.CARBON_FACTORS_CSV) -> dict[str, dict[str, Any]]:
    """Load material -> {density, gwp_per_kg, source} from the reference CSV."""
    path = Path(path)
    factors: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return factors

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or row.get("material_key", "").startswith("#"):
                continue
            k = row["material_key"].strip()
            try:
                density = float(row["density_kg_m3"]) if row.get("density_kg_m3") else None
            except ValueError:
                density = None
            try:
                gwp = float(row["gwp_per_kg_kgco2e"]) if row.get("gwp_per_kg_kgco2e") else None
            except ValueError:
                gwp = None

            factors[k] = {
                "material_category": row.get("material_category", ""),
                "density_kg_m3": density,
                "gwp_per_kg_kgco2e": gwp,
                "source": row.get("source", ""),
            }
    return factors


def enrich_carbon(item: dict[str, Any], factors: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Populate Density / Embodied Carbon A1-A3 / GWP-per-kg where defensible."""
    if factors is None:
        factors = load_factors()

    cat = item.get("material_category", "")
    unit = item.get("canonical_unit", "")
    qty = item.get("normalized_quantity")
    desc = (item.get("description") or "").lower()

    # Earthwork excavation / surface dressing -> EXCLUDED
    if cat == "Earthwork" and ("excavation" in desc or "surface dressing" in desc):
        item["density_kg_m3"] = 1600.0
        item["gwp_per_kg"] = 0.0
        item["embodied_carbon_a1_a3"] = 0.0
        item["comment"] = "[EXCLUDED] earth + labour; negligible embodied material carbon"
        return item

    # Formwork / Shuttering -> EXCLUDED
    if "shuttering" in desc or "centring" in desc:
        item["density_kg_m3"] = None
        item["gwp_per_kg"] = None
        item["embodied_carbon_a1_a3"] = None
        item["comment"] = "[EXCLUDED] temporary formwork / re-usable asset"
        return item

    # Steel reinforcement (Weight-based)
    if cat == "Reinf" or "reinforcement" in desc or "twisted bars" in desc:
        factor_info = factors.get("tmt_steel", {})
        density = factor_info.get("density_kg_m3", 7850.0)
        gwp = factor_info.get("gwp_per_kg_kgco2e", 2.363)
        mass_kg = float(qty) if qty is not None else 0.0
        ec = round(mass_kg * gwp, 3)

        item["density_kg_m3"] = density
        item["gwp_per_kg"] = gwp
        item["embodied_carbon_a1_a3"] = ec
        item["comment"] = f"[OK] deformed bar {gwp}/kg ({factor_info.get('source', 'ICE v3')})"
        return item

    # Metals & Structural Hardware (Weight or Count-based)
    if cat == "Metals / Hardware":
        factor_info = factors.get("mild_steel", {})
        density = factor_info.get("density_kg_m3", 7850.0)
        gwp = factor_info.get("gwp_per_kg_kgco2e", 2.520)
        if unit == "kg" and qty is not None:
            mass_kg = float(qty)
            ec = round(mass_kg * gwp, 3)
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = ec
            item["comment"] = f"[OK] steel section {gwp}/kg ({factor_info.get('source', 'ICE v3')})"
        else:
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = None
            item["comment"] = f"[OK] steel hardware ({factor_info.get('source', 'ICE v3')})"
        return item

    # Concrete (Volume-based)
    if cat == "Concrete" or "concrete" in desc:
        if "1:5:10" in desc:
            f_key = "concrete_1510"
        elif "1:2:4" in desc:
            f_key = "concrete_124"
        else:
            f_key = "concrete_148"
        factor_info = factors.get(f_key, factors.get("concrete_124", {}))
        density = factor_info.get("density_kg_m3", 2400.0)
        gwp = factor_info.get("gwp_per_kg_kgco2e", 0.155)

        if unit == "cum" and qty is not None:
            vol_m3 = float(qty)
            mass_kg = vol_m3 * density
            ec = round(mass_kg * gwp, 3)
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = ec
            item["comment"] = f"[OK] nominal mix concrete ({factor_info.get('source', 'ICE v3')})"
        else:
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = None
            item["comment"] = f"[OK] concrete work ({factor_info.get('source', 'ICE v3')})"
        return item

    # Masonry (Volume or Area-based)
    if cat == "Masonry" or "brick" in desc:
        factor_info = factors.get("brickwork", {})
        density = factor_info.get("density_kg_m3", 1900.0)
        gwp = factor_info.get("gwp_per_kg_kgco2e", 0.210)

        if unit == "cum" and qty is not None:
            vol_m3 = float(qty)
            mass_kg = vol_m3 * density
            ec = round(mass_kg * gwp, 3)
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = ec
            item["comment"] = f"[OK] burnt clay brickwork ({factor_info.get('source', 'ICE v3')})"
        elif unit == "sqm" and qty is not None:
            # Half-brick wall approx 0.115 m thick
            vol_m3 = float(qty) * 0.115
            mass_kg = vol_m3 * density
            ec = round(mass_kg * gwp, 3)
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = ec
            item["comment"] = f"[OK] half-brick masonry ({factor_info.get('source', 'ICE v3')})"
        else:
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = None
            item["comment"] = f"[OK] brick masonry ({factor_info.get('source', 'ICE v3')})"
        return item

    # Wood / Timber
    if cat == "Wood" or "wood" in desc or "door" in desc:
        factor_info = factors.get("timber", {})
        density = factor_info.get("density_kg_m3", 650.0)
        gwp = factor_info.get("gwp_per_kg_kgco2e", 0.450)
        if unit == "cum" and qty is not None:
            vol_m3 = float(qty)
            mass_kg = vol_m3 * density
            ec = round(mass_kg * gwp, 3)
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = ec
            item["comment"] = f"[OK] sawn timber ({factor_info.get('source', 'ICE v3')})"
        else:
            item["density_kg_m3"] = density
            item["gwp_per_kg"] = gwp
            item["embodied_carbon_a1_a3"] = None
            item["comment"] = f"[OK] wood shutters / fittings ({factor_info.get('source', 'ICE v3')})"
        return item

    # Default fallback for other items
    item["density_kg_m3"] = None
    item["gwp_per_kg"] = None
    item["embodied_carbon_a1_a3"] = None
    item["comment"] = "[OK] general item"
    return item
