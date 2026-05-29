import { useState } from "react";
import styles from "./ResultDashboard.module.css";
import CompositionChart from "../Charts/CompositionChart.jsx";
import PropertyRadar from "../Charts/PropertyRadar.jsx";
import MsdsViewer from "../MsdsViewer/MsdsViewer.jsx";
import SopDocument from "../SopDocument/SopDocument.jsx";

const TABS = [
  { id: "overview", label: "📊 Overview" },
  { id: "msds", label: "⚠️ MSDS" },
  { id: "sop", label: "📋 SOP" },
  { id: "report", label: "📄 Report" },
];

export default function ResultDashboard({ result, params, status }) {
  const [activeTab, setActiveTab] = useState("overview");

  if (!result && status !== "complete") {
    return (
      <div className={styles.dashboard}>
        <div className={styles.emptyState}>
          <img src="/images/empty_state.png" alt="Empty Lab" className={styles.emptyStateImage} />
          <div className={styles.emptyTitle}>Awaiting Results</div>
          <div className={styles.emptyDesc}>
            Run a simulation to see optimized formulation results, property predictions, and generated documentation here.
          </div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const pred = result.predictedProperties;
  const targets = params ? {
    heatResistance: params.heatResistance,
    tensileStrength: params.tensileStrength,
    ecoScore: params.ecoScore,
  } : null;

  const deltaHeat = pred.heatResistance - (params?.heatResistance || 0);
  const deltaStrength = pred.tensileStrength - (params?.tensileStrength || 0);
  const deltaEco = pred.ecoScore - (params?.ecoScore || 0);

  return (
    <div className={styles.dashboard}>
      {/* Score Card */}
      <div className={`${styles.scoreCard} glass-card`} style={{ "--score": result.score }}>
        <div className={styles.scoreCircle}>
          <div className={styles.scoreInner}>
            <span className={styles.scoreValue}>{Math.round(result.score)}</span>
            <span className={styles.scoreLabel}>Score</span>
          </div>
        </div>
        <div className={styles.scoreInfo}>
          <div className={styles.scoreTitle}>Optimization Complete</div>
          <div className={styles.scoreMeta}>
            {result.formulation.length} materials selected · {result.msdsWarnings?.length || 0} safety alerts
          </div>
          <div className={styles.catalystTag}>
            ⚗️ {result.selectedCatalyst?.name || "N/A"}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {activeTab === "overview" && (
          <>
            {/* Predicted Properties */}
            <div className={styles.propsGrid}>
              <div className={`${styles.propCard} glass-card`}>
                <span className={styles.propLabel}>Heat Resistance</span>
                <span className={styles.propValue}>
                  {pred.heatResistance}<span className={styles.propUnit}>°C</span>
                </span>
                <span className={`${styles.propDelta} ${deltaHeat >= 0 ? styles.propDeltaPositive : styles.propDeltaNegative}`}>
                  {deltaHeat >= 0 ? "+" : ""}{deltaHeat.toFixed(1)}°C vs target
                </span>
              </div>
              <div className={`${styles.propCard} glass-card`}>
                <span className={styles.propLabel}>Tensile Strength</span>
                <span className={styles.propValue}>
                  {pred.tensileStrength}<span className={styles.propUnit}> MPa</span>
                </span>
                <span className={`${styles.propDelta} ${deltaStrength >= 0 ? styles.propDeltaPositive : styles.propDeltaNegative}`}>
                  {deltaStrength >= 0 ? "+" : ""}{deltaStrength.toFixed(1)} MPa vs target
                </span>
              </div>
              <div className={`${styles.propCard} glass-card`}>
                <span className={styles.propLabel}>Eco Score</span>
                <span className={styles.propValue}>
                  {pred.ecoScore}<span className={styles.propUnit}>/100</span>
                </span>
                <span className={`${styles.propDelta} ${deltaEco >= 0 ? styles.propDeltaPositive : styles.propDeltaNegative}`}>
                  {deltaEco >= 0 ? "+" : ""}{deltaEco.toFixed(1)} vs target
                </span>
              </div>
              <div className={`${styles.propCard} glass-card`}>
                <span className={styles.propLabel}>Density</span>
                <span className={styles.propValue}>
                  {pred.density}<span className={styles.propUnit}> g/cm³</span>
                </span>
                <span className={styles.propDelta} style={{ color: "var(--text-muted)" }}>
                  Elongation: {pred.elongation}%
                </span>
              </div>
            </div>

            {/* Charts */}
            <div style={{ marginTop: "var(--sp-lg)", display: "flex", flexDirection: "column", gap: "var(--sp-lg)" }}>
              <CompositionChart formulation={result.formulation} />
              <PropertyRadar predicted={pred} targets={targets} />
            </div>

            {/* Materials List */}
            <div style={{ marginTop: "var(--sp-lg)" }}>
              <div className={styles.materialsList}>
                {result.formulation.map((f) => (
                  <div key={f.id} className={styles.materialItem}>
                    <div className={styles.materialColor} style={{ background: f.color }} />
                    <div className={styles.materialInfo}>
                      <div className={styles.materialName}>{f.name}</div>
                      <div className={styles.materialCategory}>{f.category}</div>
                    </div>
                    <span className={styles.materialRatio}>{f.ratio.toFixed(1)}%</span>
                    <span className={`${styles.hazardBadge} ${
                      f.hazardLevel === "low" ? styles.hazardBadgeLow :
                      f.hazardLevel === "medium" ? styles.hazardBadgeMedium :
                      styles.hazardBadgeHigh
                    }`}>
                      {f.hazardLevel}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === "msds" && (
          <MsdsViewer formulation={result.formulation} warnings={result.msdsWarnings} />
        )}

        {activeTab === "sop" && (
          <SopDocument content={result.sopDocument} title="Standard Operating Procedure" />
        )}

        {activeTab === "report" && (
          <SopDocument content={result.reportDocument} title="Research Report Draft" />
        )}
      </div>
    </div>
  );
}
