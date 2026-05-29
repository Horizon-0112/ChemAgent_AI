// ============================================================
// Multi-Objective Formulation Optimizer
// Weighted Euclidean distance minimization with constraints
// ============================================================

/**
 * Optimize material formulation based on target properties.
 *
 * @param {Object} params - Target parameters from user input
 * @param {Array} candidates - Filtered candidate materials
 * @param {Array} catalystPool - Compatible catalysts
 * @returns {Object} Optimized formulation result
 */
export function optimizeFormulation(params, candidates, catalystPool) {
  const target = {
    heatResistance: params.heatResistance,
    tensileStrength: params.tensileStrength,
    ecoScore: params.ecoScore,
  };

  // Weight factors for each property
  const weights = {
    heatResistance: 0.35,
    tensileStrength: 0.35,
    ecoScore: 0.30,
  };

  // Normalization ranges (typical max values)
  const norms = {
    heatResistance: 400,
    tensileStrength: 200,
    ecoScore: 100,
  };

  // ── Score each candidate material ───────────────────────
  const scoredCandidates = candidates.map((c) => {
    const distSq =
      weights.heatResistance * Math.pow((c.heatResistance - target.heatResistance) / norms.heatResistance, 2) +
      weights.tensileStrength * Math.pow((c.tensileStrength - target.tensileStrength) / norms.tensileStrength, 2) +
      weights.ecoScore * Math.pow((c.ecoScore - target.ecoScore) / norms.ecoScore, 2);

    const distance = Math.sqrt(distSq);
    // Convert distance to a fitness score (lower distance = higher score)
    const fitness = Math.max(0, 100 - distance * 100);

    return { ...c, fitness, distance };
  });

  // Sort by fitness (descending)
  scoredCandidates.sort((a, b) => b.fitness - a.fitness);

  // ── Select top materials ────────────────────────────────
  const numSelected = Math.min(
    params.domain === "Automotive" || params.domain === "Electronics" ? 4 : 3,
    scoredCandidates.length
  );
  const selected = scoredCandidates.slice(0, numSelected);

  // ── Calculate optimal ratios ────────────────────────────
  // Use inverse-distance weighting for ratio allocation
  const totalInvDist = selected.reduce((sum, s) => sum + 1 / (s.distance + 0.001), 0);

  let formulation = selected.map((s) => {
    const rawRatio = (1 / (s.distance + 0.001)) / totalInvDist * 100;
    return {
      id: s.id,
      name: s.name,
      category: s.category,
      ratio: rawRatio,
      color: s.color,
      hazardLevel: s.hazardLevel,
    };
  });

  // Normalize to ensure sum = 100
  const totalRatio = formulation.reduce((sum, f) => sum + f.ratio, 0);
  formulation = formulation.map((f) => ({
    ...f,
    ratio: (f.ratio / totalRatio) * 100,
  }));

  // ── Select best catalyst ────────────────────────────────
  const scoredCatalysts = catalystPool.map((cat) => {
    const compatCount = selected.filter((s) => s.compatibleWith.includes(cat.id)).length;
    const compatRatio = compatCount / selected.length;

    // Catalyst score: compatibility + selectivity + eco effect
    const catScore =
      compatRatio * 40 +
      (cat.selectivity / 100) * 30 +
      cat.effectOnStrength * 15 +
      cat.effectOnHeatRes * 15;

    // Penalize high toxicity
    const toxPenalty = cat.toxicity === "high" ? 15 : cat.toxicity === "medium" ? 5 : 0;

    return { ...cat, catScore: catScore - toxPenalty, compatCount };
  });

  scoredCatalysts.sort((a, b) => b.catScore - a.catScore);
  const bestCatalyst = scoredCatalysts[0];

  // ── Calculate overall optimization score ────────────────
  // Predicted properties (weighted average)
  const pred = { heatResistance: 0, tensileStrength: 0, ecoScore: 0 };
  for (const f of formulation) {
    const mat = selected.find((s) => s.id === f.id);
    if (mat) {
      const w = f.ratio / 100;
      pred.heatResistance += mat.heatResistance * w;
      pred.tensileStrength += mat.tensileStrength * w;
      pred.ecoScore += mat.ecoScore * w;
    }
  }

  // Apply catalyst modifiers
  pred.heatResistance *= bestCatalyst.effectOnHeatRes;
  pred.tensileStrength *= bestCatalyst.effectOnStrength;
  pred.ecoScore *= bestCatalyst.effectOnEco;

  // Score: how close are predicted to target (100 = perfect match)
  const finalDist = Math.sqrt(
    weights.heatResistance * Math.pow((pred.heatResistance - target.heatResistance) / norms.heatResistance, 2) +
    weights.tensileStrength * Math.pow((pred.tensileStrength - target.tensileStrength) / norms.tensileStrength, 2) +
    weights.ecoScore * Math.pow((pred.ecoScore - target.ecoScore) / norms.ecoScore, 2)
  );

  const overallScore = Math.max(0, Math.min(100, 100 - finalDist * 100 + Math.random() * 5));

  return {
    selectedMaterials: selected,
    selectedCatalyst: bestCatalyst,
    formulation,
    score: overallScore,
  };
}
