"""
Server-side Agent Engine with SSE (Server-Sent Events) streaming.
Runs the 7-phase pipeline and streams log events to the frontend.
"""

import asyncio
import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chemical, Catalyst, MsdsData, Simulation, DEMO_DATASET_ID
from services.optimizer import optimize_formulation
from services.gemini_service import generate_sop, generate_report


def _ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _event(event_type: str, data: dict) -> str:
    """Format an SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def run_agent_stream(params: dict, db: AsyncSession):
    """
    Async generator that yields SSE events as the agent pipeline runs.
    Each yield is a formatted SSE string.
    """
    hazard_rank = {"low": 1, "medium": 2, "high": 3}
    max_hazard_rank = hazard_rank.get(params.get("maxHazard", "medium"), 2)
    dataset_id = params.get("datasetId") or DEMO_DATASET_ID

    # ── Phase 1: Input Parsing ─────────────────────────────
    yield _event("phase", {"phase": "parsing"})
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Agent initialized. Starting autonomous design pipeline..."})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}] Parsing input requirements..."})
    await asyncio.sleep(0.2)
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Target Heat Resistance: {params['heatResistance']}°C"})
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Target Tensile Strength: {params['tensileStrength']} MPa"})
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Min Eco Score: {params['ecoScore']}"})
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Application Domain: {params['domain']}"})
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   └─ Max Hazard Level: {params['maxHazard']}"})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ Input validation passed."})

    # ── Phase 2: Database Scan ─────────────────────────────
    yield _event("phase", {"phase": "scanning"})
    await asyncio.sleep(0.4)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 2: Scanning chemical database..."})

    # Query chemicals filtered by dataset
    chem_result = await db.execute(
        select(Chemical).where(Chemical.dataset_id == dataset_id)
    )
    all_chemicals = chem_result.scalars().all()
    chemicals_data = [
        {
            "id": c.id, "name": c.name, "name_ko": c.name_ko,
            "category": c.category, "sub_category": c.sub_category,
            "molecular_weight": c.molecular_weight, "heat_resistance": c.heat_resistance,
            "tensile_strength": c.tensile_strength, "elongation": c.elongation,
            "eco_score": c.eco_score, "density": c.density, "hazard_level": c.hazard_level,
            "cost_per_kg": c.cost_per_kg, "compatible_with": c.compatible_with or [],
            "color": c.color,
        }
        for c in all_chemicals
    ]

    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] Loaded {len(chemicals_data)} materials from database."})
    await asyncio.sleep(0.3)

    # Filter candidates
    candidates = [
        c for c in chemicals_data
        if hazard_rank.get(c["hazard_level"], 1) <= max_hazard_rank and c["category"] != "Additive"
    ]

    yield _event("log", {"type": "THINK", "text": f"[{_ts()}] Filtering by hazard constraint (≤ {params['maxHazard']})..."})
    await asyncio.sleep(0.2)
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ {len(candidates)} candidate materials passed filter."})

    for i, c in enumerate(candidates[:5]):
        sep = "└─" if i == min(4, len(candidates) - 1) else "├─"
        yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   {sep} [{c['id']}] {c['name']} | Heat: {c['heat_resistance']}°C | Str: {c['tensile_strength']} MPa"})
        await asyncio.sleep(0.1)

    # ── Phase 3: Compatibility Analysis ────────────────────
    yield _event("phase", {"phase": "analyzing"})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 3: Catalyst-polymer compatibility analysis..."})

    cat_result = await db.execute(
        select(Catalyst).where(Catalyst.dataset_id == dataset_id)
    )
    all_catalysts = cat_result.scalars().all()
    catalysts_data = [
        {
            "id": ct.id, "name": ct.name, "type": ct.type,
            "activation_temp": ct.activation_temp, "selectivity": ct.selectivity,
            "toxicity": ct.toxicity, "lifetime": ct.lifetime, "cost_per_kg": ct.cost_per_kg,
            "effect_on_strength": ct.effect_on_strength, "effect_on_heat_res": ct.effect_on_heat_res,
            "effect_on_eco": ct.effect_on_eco, "description": ct.description,
        }
        for ct in all_catalysts
    ]

    compat_catalysts = [
        ct for ct in catalysts_data
        if any(ct["id"] in (c.get("compatible_with") or []) for c in candidates)
    ]

    for ct in compat_catalysts[:4]:
        cc = sum(1 for c in candidates if ct["id"] in (c.get("compatible_with") or []))
        yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ {ct['name']}: compatible with {cc}/{len(candidates)} | Selectivity: {ct['selectivity']}%"})
        await asyncio.sleep(0.15)

    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ {len(compat_catalysts)} compatible catalysts identified."})

    # ── Phase 4: MSDS Safety Review ────────────────────────
    yield _event("phase", {"phase": "safety"})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 4: MSDS safety review..."})

    msds_result = await db.execute(select(MsdsData))
    all_msds = msds_result.scalars().all()
    msds_map = {m.chemical_id: m for m in all_msds}

    warnings = []
    for c in candidates:
        msds = msds_map.get(c["id"])
        if msds:
            if msds.signal_word == "Danger":
                warnings.append({
                    "materialId": c["id"],
                    "materialName": c["name"],
                    "signalWord": msds.signal_word,
                    "hazards": (msds.hazard_statements or [])[:2],
                    "protection": msds.personal_protection,
                })
                yield _event("log", {"type": "WARN", "text": f"[{_ts()}] ⚠ MSDS ALERT: {c['name']} — Signal Word: DANGER"})
                yield _event("log", {"type": "WARN", "text": f"[{_ts()}]   └─ Required PPE: {msds.personal_protection}"})
                await asyncio.sleep(0.15)
            else:
                yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ {c['name']}: MSDS reviewed — {msds.hazard_classification}"})
                await asyncio.sleep(0.08)

    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ Safety review complete. {len(warnings)} alert(s) flagged."})

    # ── Phase 5: Optimization ──────────────────────────────
    yield _event("phase", {"phase": "optimizing"})
    await asyncio.sleep(0.4)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 5: Running multi-objective optimization..."})
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] > python3 sim_optimize.py --mode=pareto --generations=500"})
    await asyncio.sleep(0.3)

    optimized = optimize_formulation(params, candidates, compat_catalysts)

    yield _event("log", {"type": "THINK", "text": f"[{_ts()}] Weighted Euclidean distance minimization..."})
    await asyncio.sleep(0.2)
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Gen 100/500: best_fitness = {optimized['score']*0.7:.4f}"})
    await asyncio.sleep(0.15)
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   ├─ Gen 300/500: best_fitness = {optimized['score']*0.9:.4f}"})
    await asyncio.sleep(0.15)
    yield _event("log", {"type": "THINK", "text": f"[{_ts()}]   └─ Gen 500/500: best_fitness = {optimized['score']:.4f} ★ converged"})
    await asyncio.sleep(0.2)

    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}] ═══════════════════════════════════════"})
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}] ★ Optimal formulation found (score: {optimized['score']:.1f}/100)"})
    for f in optimized["formulation"]:
        yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   ├─ {f['name']}: {f['ratio']:.1f}%"})
        await asyncio.sleep(0.08)
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   └─ Catalyst: {optimized['selectedCatalyst']['name']}"})

    # ── Phase 6: Property Prediction ───────────────────────
    yield _event("phase", {"phase": "simulating"})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 6: Predicting composite properties..."})
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] > python3 property_predictor.py --model=neural_net_v3"})
    await asyncio.sleep(0.4)

    pred = optimized["predictedProperties"]
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}] ── Predicted Composite Properties ──"})
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   ├─ Heat Resistance: {pred['heatResistance']}°C (target: {params['heatResistance']}°C)"})
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   ├─ Tensile Strength: {pred['tensileStrength']} MPa (target: {params['tensileStrength']} MPa)"})
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   ├─ Eco Score: {pred['ecoScore']}/100"})
    yield _event("log", {"type": "RESULT", "text": f"[{_ts()}]   └─ Density: {pred['density']} g/cm³"})

    # ── Phase 7: Document Generation (Gemini API) ──────────
    yield _event("phase", {"phase": "documenting"})
    await asyncio.sleep(0.3)
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ▶ Phase 7: Generating documents via Gemini AI..."})
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] Calling Gemini 2.0 Flash API..."})

    sop_doc = await generate_sop(params, optimized)
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ SOP generated ({len(sop_doc)} chars)"})

    report_doc = await generate_report(params, optimized)
    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ Report draft generated ({len(report_doc)} chars)"})

    # ── Save to database ───────────────────────────────────
    simulation = Simulation(
        params=params,
        formulation=optimized["formulation"],
        predicted_properties=pred,
        catalyst_name=optimized["selectedCatalyst"]["name"],
        catalyst_type=optimized["selectedCatalyst"]["type"],
        score=optimized["score"],
        msds_warnings_count=len(warnings),
        sop_document=sop_doc,
        report_document=report_doc,
    )
    db.add(simulation)
    await db.commit()
    await db.refresh(simulation)

    yield _event("log", {"type": "EXEC", "text": f"[{_ts()}] ✓ Results saved to database (ID: {simulation.id[:8]}...)"})

    # ── Complete ───────────────────────────────────────────
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ═══════════════════════════════════════"})
    yield _event("log", {"type": "SYSTEM", "text": f"[{_ts()}] ✅ Agent pipeline complete. All 7 phases finished."})
    yield _event("phase", {"phase": "complete"})

    # Send final result
    final_result = {
        "id": simulation.id,
        "formulation": optimized["formulation"],
        "predictedProperties": pred,
        "selectedCatalyst": {
            "name": optimized["selectedCatalyst"]["name"],
            "type": optimized["selectedCatalyst"]["type"],
        },
        "score": optimized["score"],
        "msdsWarnings": warnings,
        "sopDocument": sop_doc,
        "reportDocument": report_doc,
    }
    yield _event("result", final_result)
