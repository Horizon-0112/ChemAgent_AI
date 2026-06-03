// ============================================================
// Agent Reasoning Engine - Core Pipeline
// Simulates AI agent's autonomous reasoning and analysis process
// ============================================================

import chemicals from "../data/chemicals.js";
import catalysts from "../data/catalysts.js";
import msdsData from "../data/msds.js";
import { optimizeFormulation } from "./optimizer.js";
import { generateSOP } from "./sopGenerator.js";

/**
 * Delay helper for simulating async processing
 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Generate a timestamp string for log entries
 */
const timestamp = () => {
  const now = new Date();
  return now.toLocaleTimeString("en-US", { hour12: false, fractionalSecondDigits: 3 });
};

/**
 * Main Agent Pipeline
 * Runs through 7 sequential reasoning phases, emitting logs via callback
 *
 * @param {Object} params - User input parameters
 * @param {Function} onLog - Callback for streaming log messages
 * @param {Function} onPhaseChange - Callback for phase transitions
 * @returns {Object} Final result with formulation, predictions, SOP
 */
export async function runAgentPipeline(params, onLog, onPhaseChange) {
  const result = {
    selectedMaterials: [],
    selectedCatalyst: null,
    formulation: [],
    predictedProperties: {},
    msdsWarnings: [],
    sopDocument: "",
    reportDocument: "",
    score: 0,
  };

  try {
    // ── Phase 1: Input Parsing ─────────────────────────────
    onPhaseChange("parsing");
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Agent initialized. Starting autonomous design pipeline...` });
    await delay(400);
    onLog({ type: "THINK", text: `[${timestamp()}] Parsing input requirements...` });
    await delay(300);
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Target Heat Resistance: ${params.heatResistance}°C` });
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Target Tensile Strength: ${params.tensileStrength} MPa` });
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Min Eco Score: ${params.ecoScore}` });
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Application Domain: ${params.domain}` });
    onLog({ type: "THINK", text: `[${timestamp()}]   └─ Max Hazard Level: ${params.maxHazard}` });
    await delay(500);
    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ Input validation passed. Constraints loaded.` });

    // ── Phase 2: Database Scan ─────────────────────────────
    onPhaseChange("scanning");
    await delay(600);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 2: Scanning chemical database...` });
    await delay(300);
    onLog({ type: "EXEC", text: `[${timestamp()}] Loading ${chemicals.length} materials from virtual database...` });
    await delay(400);

    // Filter candidates by hazard level
    const hazardRank = { low: 1, medium: 2, high: 3 };
    const maxHazardRank = hazardRank[params.maxHazard] || 2;

    const candidates = chemicals.filter((c) => {
      return hazardRank[c.hazardLevel] <= maxHazardRank && c.category !== "Additive";
    });

    onLog({ type: "THINK", text: `[${timestamp()}] Filtering by hazard constraint (≤ ${params.maxHazard})...` });
    await delay(300);
    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ ${candidates.length} candidate materials passed hazard filter.` });
    await delay(200);

    // Log some candidates
    for (let i = 0; i < Math.min(5, candidates.length); i++) {
      onLog({
        type: "THINK",
        text: `[${timestamp()}]   ${i === Math.min(5, candidates.length) - 1 ? "└─" : "├─"} [${candidates[i].id}] ${candidates[i].name} | Heat: ${candidates[i].heatResistance}°C | Strength: ${candidates[i].tensileStrength} MPa`,
      });
      await delay(150);
    }
    if (candidates.length > 5) {
      onLog({ type: "THINK", text: `[${timestamp()}]      ... and ${candidates.length - 5} more candidates` });
    }

    // ── Phase 3: Compatibility Analysis ────────────────────
    onPhaseChange("analyzing");
    await delay(500);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 3: Catalyst-polymer compatibility analysis...` });
    await delay(400);

    // Find compatible catalysts
    const compatibleCatalysts = catalysts.filter((cat) => {
      return candidates.some((c) => c.compatibleWith.includes(cat.id));
    });

    for (const cat of compatibleCatalysts.slice(0, 4)) {
      const compatCount = candidates.filter((c) => c.compatibleWith.includes(cat.id)).length;
      onLog({
        type: "THINK",
        text: `[${timestamp()}]   ├─ ${cat.name}: compatible with ${compatCount}/${candidates.length} candidates | Selectivity: ${cat.selectivity}%`,
      });
      await delay(200);
    }

    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ ${compatibleCatalysts.length} compatible catalysts identified.` });

    // ── Phase 4: MSDS Safety Review ────────────────────────
    onPhaseChange("safety");
    await delay(500);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 4: MSDS safety review...` });
    await delay(400);

    const warnings = [];
    for (const cand of candidates) {
      const msds = msdsData.find((m) => m.chemicalId === cand.id);
      if (msds) {
        if (msds.signalWord === "Danger") {
          warnings.push({
            materialId: cand.id,
            materialName: cand.name,
            signalWord: msds.signalWord,
            hazards: msds.hazardStatements.slice(0, 2),
            protection: msds.personalProtection,
          });
          onLog({
            type: "WARN",
            text: `[${timestamp()}] ⚠ MSDS ALERT: ${cand.name} — Signal Word: DANGER`,
          });
          await delay(200);
          onLog({
            type: "WARN",
            text: `[${timestamp()}]   └─ Required PPE: ${msds.personalProtection}`,
          });
          await delay(150);
        } else {
          onLog({
            type: "THINK",
            text: `[${timestamp()}]   ├─ ${cand.name}: MSDS reviewed — ${msds.hazardClassification}`,
          });
          await delay(100);
        }
      }
    }

    result.msdsWarnings = warnings;
    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ Safety review complete. ${warnings.length} hazard alert(s) flagged.` });

    // ── Phase 5: Formulation Optimization ──────────────────
    onPhaseChange("optimizing");
    await delay(600);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 5: Running multi-objective optimization...` });
    await delay(300);
    onLog({ type: "EXEC", text: `[${timestamp()}] Executing optimization script...` });
    onLog({ type: "EXEC", text: `[${timestamp()}] > python3 sim_optimize.py --mode=pareto --generations=500` });
    await delay(500);

    const optimized = optimizeFormulation(params, candidates, compatibleCatalysts);

    onLog({ type: "THINK", text: `[${timestamp()}] Weighted Euclidean distance minimization...` });
    await delay(300);
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Generation 100/500: best_fitness = ${(optimized.score * 0.7).toFixed(4)}` });
    await delay(200);
    onLog({ type: "THINK", text: `[${timestamp()}]   ├─ Generation 300/500: best_fitness = ${(optimized.score * 0.9).toFixed(4)}` });
    await delay(200);
    onLog({ type: "THINK", text: `[${timestamp()}]   └─ Generation 500/500: best_fitness = ${optimized.score.toFixed(4)} ★ converged` });
    await delay(300);

    result.selectedMaterials = optimized.selectedMaterials;
    result.selectedCatalyst = optimized.selectedCatalyst;
    result.formulation = optimized.formulation;
    result.score = optimized.score;

    onLog({ type: "RESULT", text: `[${timestamp()}] ═══════════════════════════════════════` });
    onLog({ type: "RESULT", text: `[${timestamp()}] ★ Optimal formulation found (score: ${optimized.score.toFixed(2)}/100)` });
    for (const f of optimized.formulation) {
      onLog({
        type: "RESULT",
        text: `[${timestamp()}]   ├─ ${f.name}: ${f.ratio.toFixed(1)}%`,
      });
      await delay(100);
    }
    onLog({
      type: "RESULT",
      text: `[${timestamp()}]   └─ Catalyst: ${optimized.selectedCatalyst.name}`,
    });

    // ── Phase 6: Property Prediction ───────────────────────
    onPhaseChange("simulating");
    await delay(500);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 6: Predicting composite properties...` });
    await delay(300);
    onLog({ type: "EXEC", text: `[${timestamp()}] > python3 property_predictor.py --model=neural_net_v3` });
    await delay(600);

    // Calculate predicted properties via weighted average
    const predicted = {
      heatResistance: 0,
      tensileStrength: 0,
      elongation: 0,
      ecoScore: 0,
      density: 0,
    };

    for (const f of optimized.formulation) {
      const mat = chemicals.find((c) => c.id === f.id);
      if (mat) {
        const w = f.ratio / 100;
        predicted.heatResistance += mat.heatResistance * w;
        predicted.tensileStrength += mat.tensileStrength * w;
        predicted.elongation += mat.elongation * w;
        predicted.ecoScore += mat.ecoScore * w;
        predicted.density += mat.density * w;
      }
    }

    // Apply catalyst effects
    const cat = optimized.selectedCatalyst;
    predicted.heatResistance *= cat.effectOnHeatRes;
    predicted.tensileStrength *= cat.effectOnStrength;
    predicted.ecoScore *= cat.effectOnEco;

    // Round values
    Object.keys(predicted).forEach((key) => {
      predicted[key] = Math.round(predicted[key] * 10) / 10;
    });

    result.predictedProperties = predicted;

    onLog({ type: "RESULT", text: `[${timestamp()}] ── Predicted Composite Properties ──` });
    onLog({ type: "RESULT", text: `[${timestamp()}]   ├─ Heat Resistance: ${predicted.heatResistance}°C (target: ${params.heatResistance}°C)` });
    onLog({ type: "RESULT", text: `[${timestamp()}]   ├─ Tensile Strength: ${predicted.tensileStrength} MPa (target: ${params.tensileStrength} MPa)` });
    onLog({ type: "RESULT", text: `[${timestamp()}]   ├─ Elongation: ${predicted.elongation}%` });
    onLog({ type: "RESULT", text: `[${timestamp()}]   ├─ Eco Score: ${predicted.ecoScore}/100` });
    onLog({ type: "RESULT", text: `[${timestamp()}]   └─ Density: ${predicted.density} g/cm³` });

    // ── Phase 7: SOP Generation ────────────────────────────
    onPhaseChange("documenting");
    await delay(500);
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ▶ Phase 7: Generating SOP & Report documents...` });
    await delay(400);
    onLog({ type: "EXEC", text: `[${timestamp()}] Compiling Standard Operating Procedure...` });
    await delay(600);

    const sopDoc = generateSOP(params, result);
    result.sopDocument = sopDoc.sop;
    result.reportDocument = sopDoc.report;

    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ SOP document generated (${sopDoc.sop.length} chars)` });
    await delay(200);
    onLog({ type: "EXEC", text: `[${timestamp()}] ✓ Report draft generated (${sopDoc.report.length} chars)` });
    await delay(300);

    onLog({ type: "SYSTEM", text: `[${timestamp()}] ═══════════════════════════════════════` });
    onLog({ type: "SYSTEM", text: `[${timestamp()}] ✅ Agent pipeline complete. All phases finished successfully.` });
    onLog({ type: "SYSTEM", text: `[${timestamp()}] Total materials analyzed: ${chemicals.length}` });
    onLog({ type: "SYSTEM", text: `[${timestamp()}] Optimization score: ${result.score.toFixed(2)}/100` });

    onPhaseChange("complete");
    return result;
  } catch (err) {
    onLog({ type: "ERROR", text: `[${timestamp()}] ✗ Agent error: ${err.message}` });
    onPhaseChange("error");
    throw err;
  }
}
