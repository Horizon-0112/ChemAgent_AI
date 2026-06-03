"""
Multi-objective formulation optimizer (Python port).
Weighted Euclidean distance minimization with constraint handling.
"""

import math


def optimize_formulation(params: dict, candidates: list, catalyst_pool: list) -> dict:
    """
    Optimize material formulation based on target properties.

    Args:
        params: Target parameters (heatResistance, tensileStrength, ecoScore, domain, maxHazard)
        candidates: Filtered candidate materials (list of dicts)
        catalyst_pool: Compatible catalysts (list of dicts)

    Returns:
        dict with selectedMaterials, selectedCatalyst, formulation, score
    """
    target = {
        "heatResistance": params["heatResistance"],
        "tensileStrength": params["tensileStrength"],
        "ecoScore": params["ecoScore"],
    }

    weights = {"heatResistance": 0.35, "tensileStrength": 0.35, "ecoScore": 0.30}
    norms = {"heatResistance": 400, "tensileStrength": 200, "ecoScore": 100}

    # Score each candidate
    scored = []
    for c in candidates:
        dist_sq = (
            weights["heatResistance"] * ((c["heat_resistance"] - target["heatResistance"]) / norms["heatResistance"]) ** 2
            + weights["tensileStrength"] * ((c["tensile_strength"] - target["tensileStrength"]) / norms["tensileStrength"]) ** 2
            + weights["ecoScore"] * ((c["eco_score"] - target["ecoScore"]) / norms["ecoScore"]) ** 2
        )
        distance = math.sqrt(dist_sq)
        fitness = max(0, 100 - distance * 100)
        scored.append({**c, "fitness": fitness, "distance": distance})

    scored.sort(key=lambda x: x["fitness"], reverse=True)

    # Select top materials
    domain = params.get("domain", "")
    num_select = min(4 if domain in ("Automotive", "Electronics") else 3, len(scored))
    selected = scored[:num_select]

    # Inverse-distance ratio allocation
    total_inv = sum(1 / (s["distance"] + 0.001) for s in selected)
    formulation = []
    for s in selected:
        raw_ratio = (1 / (s["distance"] + 0.001)) / total_inv * 100
        formulation.append({
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "ratio": raw_ratio,
            "color": s["color"],
            "hazardLevel": s["hazard_level"],
        })

    # Normalize to 100%
    total_ratio = sum(f["ratio"] for f in formulation)
    for f in formulation:
        f["ratio"] = (f["ratio"] / total_ratio) * 100

    # Score catalysts
    cat_scored = []
    for cat in catalyst_pool:
        compat_count = sum(1 for s in selected if cat["id"] in (s.get("compatible_with") or []))
        compat_ratio = compat_count / len(selected) if selected else 0

        cat_score = (
            compat_ratio * 40
            + (cat["selectivity"] / 100) * 30
            + cat["effect_on_strength"] * 15
            + cat["effect_on_heat_res"] * 15
        )
        tox_penalty = 15 if cat["toxicity"] == "high" else 5 if cat["toxicity"] == "medium" else 0
        cat_scored.append({**cat, "catScore": cat_score - tox_penalty, "compatCount": compat_count})

    cat_scored.sort(key=lambda x: x["catScore"], reverse=True)
    best_catalyst = cat_scored[0] if cat_scored else None

    # Predicted properties
    pred = {"heatResistance": 0, "tensileStrength": 0, "ecoScore": 0, "elongation": 0, "density": 0}
    for f in formulation:
        mat = next((s for s in selected if s["id"] == f["id"]), None)
        if mat:
            w = f["ratio"] / 100
            pred["heatResistance"] += mat["heat_resistance"] * w
            pred["tensileStrength"] += mat["tensile_strength"] * w
            pred["ecoScore"] += mat["eco_score"] * w
            pred["elongation"] += mat["elongation"] * w
            pred["density"] += mat["density"] * w

    if best_catalyst:
        pred["heatResistance"] *= best_catalyst["effect_on_heat_res"]
        pred["tensileStrength"] *= best_catalyst["effect_on_strength"]
        pred["ecoScore"] *= best_catalyst["effect_on_eco"]

    for k in pred:
        pred[k] = round(pred[k], 1)

    # Overall score
    final_dist = math.sqrt(
        weights["heatResistance"] * ((pred["heatResistance"] - target["heatResistance"]) / norms["heatResistance"]) ** 2
        + weights["tensileStrength"] * ((pred["tensileStrength"] - target["tensileStrength"]) / norms["tensileStrength"]) ** 2
        + weights["ecoScore"] * ((pred["ecoScore"] - target["ecoScore"]) / norms["ecoScore"]) ** 2
    )
    overall_score = max(0, min(100, 100 - final_dist * 100))

    return {
        "selectedMaterials": selected,
        "selectedCatalyst": best_catalyst,
        "formulation": formulation,
        "predictedProperties": pred,
        "score": overall_score,
    }
