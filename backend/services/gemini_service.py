"""
Gemini API integration for SOP and Report document generation.
Uses Google GenAI SDK to call Gemini 2.0 Flash.
"""

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


def get_client():
    """Create a Gemini client."""
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


async def generate_sop(params: dict, result: dict) -> str:
    """
    Generate a Standard Operating Procedure using Gemini API.
    Falls back to template if API key is not available.
    """
    client = get_client()
    if not client:
        return _template_sop(params, result)

    formulation_text = "\n".join(
        f"- {f['name']} ({f['category']}): {f['ratio']:.1f}% [Hazard: {f['hazardLevel']}]"
        for f in result["formulation"]
    )
    pred = result["predictedProperties"]
    catalyst = result["selectedCatalyst"]

    prompt = f"""You are a Senior Polymer Research Scientist. Generate a highly professional, detailed Standard Operating Procedure (SOP) 
in Markdown format for the following optimized polymer composite formulation.

## Design Parameters
- Target Heat Resistance: {params['heatResistance']}°C
- Target Tensile Strength: {params['tensileStrength']} MPa
- Min Eco Score: {params['ecoScore']}/100
- Application Domain: {params['domain']}
- Max Hazard Level: {params['maxHazard']}

## Optimized Formulation (Score: {result['score']:.1f}/100)
{formulation_text}

## Selected Catalyst
- Name: {catalyst['name']}
- Type: {catalyst['type']}
- Activation Temperature: {catalyst['activation_temp']}°C
- Selectivity: {catalyst['selectivity']}%
- Toxicity: {catalyst['toxicity']}

## Predicted Properties
- Heat Resistance: {pred['heatResistance']}°C
- Tensile Strength: {pred['tensileStrength']} MPa
- Elongation: {pred['elongation']}%
- Eco Score: {pred['ecoScore']}/100
- Density: {pred['density']} g/cm³

Write a comprehensive SOP including:
1. Document header with SOP ID and date
2. Scientific Objective & Scope
3. Materials & Equipment (with exact quantities for a 200g batch)
4. Curing Kinetics & Gelation Control: Briefly explain the activation mechanism of {catalyst['name']} and how to control the exotherm.
5. Detailed step-by-step experimental procedure (preparation, weighing, mixing, reaction kinetics control, molding, testing)
6. Safety precautions based on the hazard levels
7. Expected results table comparing targets vs predictions
8. Pass/fail criteria & Quality Assurance

Use highly professional scientific language suitable for an advanced R&D laboratory. Format with proper Markdown headings, tables, and bullet points. Ensure the procedure reflects realistic laboratory practices for polymer synthesis.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _template_sop(params, result)


async def generate_report(params: dict, result: dict) -> str:
    """
    Generate a research report draft using Gemini API.
    Falls back to template if API key is not available.
    """
    client = get_client()
    if not client:
        return _template_report(params, result)

    formulation_text = "\n".join(
        f"- {f['name']}: {f['ratio']:.1f}%"
        for f in result["formulation"]
    )
    pred = result["predictedProperties"]

    prompt = f"""You are a Senior R&D Materials Scientist. Write a comprehensive research report draft in Markdown format 
for an AI-optimized polymer composite formulation experiment. The report must read like a peer-reviewed academic paper or a top-tier industrial R&D whitepaper.

## Design Requirements
- Heat Resistance: {params['heatResistance']}°C | Tensile Strength: {params['tensileStrength']} MPa | Eco Score: ≥{params['ecoScore']}
- Domain: {params['domain']} | Max Hazard: {params['maxHazard']}

## Formulation (Score: {result['score']:.1f}/100)
{formulation_text}
Catalyst: {result['selectedCatalyst']['name']} ({result['selectedCatalyst']['type']})

## Predicted Results
Heat Res: {pred['heatResistance']}°C | Strength: {pred['tensileStrength']} MPa | Eco: {pred['ecoScore']} | Density: {pred['density']} g/cm³

Write the report including:
1. Executive Summary
2. Molecular & Curing Mechanics: Detail the theoretical crosslinking behaviors, activation pathways of the catalyst, and molecular interactions of the composite.
3. Structure-Property Relationships: Scientifically justify how the specific formulation ratios achieve the predicted heat resistance and tensile strength.
4. Methodology (7-phase AI optimization pipeline overview)
5. Results (formulation table, predicted vs target comparison)
6. R&D Discussion & Future Works: Discuss potential scale-up bottlenecks, thermodynamic considerations during bulk curing, and environmental/toxicity impact mitigation. 
7. Safety Assessment & Recommendations

Use advanced scientific tone. Include Markdown tables for data. Ensure the content provides a solid foundational draft that a senior researcher can further edit and refine.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _template_report(params, result)


def _template_sop(params: dict, result: dict) -> str:
    """Fallback template when Gemini API is unavailable."""
    from datetime import datetime
    now = datetime.now()
    pred = result["predictedProperties"]
    cat = result["selectedCatalyst"]

    rows = "\n".join(
        f"| {i+1} | {f['name']} | {f['category']} | {f['ratio']:.1f}% | {f['hazardLevel'].upper()} |"
        for i, f in enumerate(result["formulation"])
    )

    return f"""# Standard Operating Procedure (SOP)
## Polymer Composite Formulation — Experimental Guide

| Field | Detail |
|-------|--------|
| **Document ID** | SOP-{now.strftime('%Y%m%d')}-AUTO |
| **Date** | {now.strftime('%Y-%m-%d')} |
| **Generated by** | ChemAgent AI (Template Mode) |
| **Application Domain** | {params['domain']} |
| **Optimization Score** | {result['score']:.1f} / 100 |

> ⚠️ This SOP was generated using a template fallback. For AI-generated content, configure your Gemini API key.

---

## 1. Objective

Design and synthesize a polymer composite optimized for:

| Property | Target |
|----------|--------|
| Heat Resistance | {params['heatResistance']}°C |
| Tensile Strength | {params['tensileStrength']} MPa |
| Eco Score | ≥ {params['ecoScore']} / 100 |

## 2. Materials

| # | Material | Category | Ratio | Hazard |
|---|----------|----------|-------|--------|
{rows}

**Catalyst**: {cat['name']} ({cat['type']}) — Activation: {cat['activation_temp']}°C

## 3. Expected Results

| Property | Target | Predicted |
|----------|--------|-----------|
| Heat Resistance | {params['heatResistance']}°C | {pred['heatResistance']}°C |
| Tensile Strength | {params['tensileStrength']} MPa | {pred['tensileStrength']} MPa |
| Eco Score | ≥{params['ecoScore']} | {pred['ecoScore']} |
| Density | — | {pred['density']} g/cm³ |

---
*Generated: {now.strftime('%Y-%m-%d %H:%M')} — Template Mode*
"""


def _template_report(params: dict, result: dict) -> str:
    """Fallback report template."""
    from datetime import datetime
    now = datetime.now()
    pred = result["predictedProperties"]

    rows = "\n".join(
        f"| {f['name']} | {f['ratio']:.1f}% | {f['category']} |"
        for f in result["formulation"]
    )

    return f"""# Research Report Draft

**Report ID**: RPT-{now.strftime('%Y%m%d')}-AUTO
**Date**: {now.strftime('%Y-%m-%d')}

> ⚠️ Template mode. Configure Gemini API key for AI-generated reports.

## Executive Summary

A {len(result['formulation'])}-component formulation was identified with an optimization score of **{result['score']:.1f}/100** for {params['domain']} applications.

## Formulation

| Material | Ratio | Category |
|----------|-------|----------|
{rows}

## Predicted vs Target

| Property | Target | Predicted | Delta |
|----------|--------|-----------|-------|
| Heat Resistance | {params['heatResistance']}°C | {pred['heatResistance']}°C | {pred['heatResistance'] - params['heatResistance']:.1f}°C |
| Tensile Strength | {params['tensileStrength']} MPa | {pred['tensileStrength']} MPa | {pred['tensileStrength'] - params['tensileStrength']:.1f} MPa |
| Eco Score | ≥{params['ecoScore']} | {pred['ecoScore']} | {pred['ecoScore'] - params['ecoScore']:.1f} |

---
*Generated: {now.strftime('%Y-%m-%d %H:%M')} — Template Mode*
"""
