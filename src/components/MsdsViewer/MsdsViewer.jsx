import { useState } from "react";
import msdsData from "../../data/msds.js";
import styles from "./MsdsViewer.module.css";

export default function MsdsViewer({ formulation, warnings }) {
  const [openId, setOpenId] = useState(null);

  const toggle = (id) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  if (!formulation || formulation.length === 0) {
    return <div className={styles.noData}>No materials selected yet.</div>;
  }

  return (
    <div className={styles.viewer}>
      {/* Warning Banner */}
      {warnings && warnings.length > 0 && (
        <div className={styles.warningBanner}>
          <span className={styles.warningIcon}>🚨</span>
          <span className={styles.warningText}>
            {warnings.length} material(s) flagged with elevated hazard levels. Review MSDS details below.
          </span>
        </div>
      )}

      {/* Material Accordion */}
      {formulation.map((f) => {
        const msds = msdsData.find((m) => m.chemicalId === f.id);
        const isOpen = openId === f.id;
        const hasWarning = warnings?.some((w) => w.materialId === f.id);

        return (
          <div key={f.id} className={styles.materialSection}>
            <div className={styles.materialHeader} onClick={() => toggle(f.id)}>
              <div className={styles.materialHeaderLeft}>
                <span style={{ color: f.color, fontSize: "14px" }}>●</span>
                <span className={styles.materialHeaderName}>
                  {f.name}
                  {hasWarning && " ⚠️"}
                </span>
              </div>
              <span className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ""}`}>
                ▶
              </span>
            </div>

            {isOpen && msds && (
              <div className={styles.msdsContent}>
                {/* Classification */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>Hazard Classification</span>
                  <span className={styles.msdsValue}>{msds.hazardClassification}</span>
                </div>

                {/* GHS Symbols */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>GHS Pictograms</span>
                  <div className={styles.ghsBadges}>
                    {msds.ghsSymbols.map((s) => (
                      <span key={s} className={styles.ghsBadge}>{s}</span>
                    ))}
                    <span className={styles.ghsBadge} style={{
                      background: msds.signalWord === "위험" ? "rgba(255,82,82,0.15)" : "rgba(255,215,64,0.15)",
                      color: msds.signalWord === "위험" ? "var(--accent-red)" : "var(--accent-yellow)",
                      borderColor: msds.signalWord === "위험" ? "rgba(255,82,82,0.3)" : "rgba(255,215,64,0.3)",
                    }}>
                      {msds.signalWord}
                    </span>
                  </div>
                </div>

                {/* Hazard Statements */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>Hazard Statements</span>
                  <ul className={styles.hazardList}>
                    {msds.hazardStatements.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </div>

                {/* First Aid */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>First Aid Measures</span>
                  <div className={styles.firstAidGrid}>
                    {Object.entries(msds.firstAid).map(([type, text]) => (
                      <div key={type} className={styles.firstAidItem}>
                        <div className={styles.firstAidType}>{type}</div>
                        <div className={styles.firstAidText}>{text}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Storage */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>Storage Conditions</span>
                  <span className={styles.msdsValue}>{msds.storageConditions}</span>
                </div>

                {/* PPE */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>Required PPE</span>
                  <span className={styles.msdsValue}>{msds.personalProtection}</span>
                </div>

                {/* Emergency */}
                <div className={styles.msdsRow}>
                  <span className={styles.msdsLabel}>Emergency Measures</span>
                  <span className={styles.msdsValue}>{msds.emergencyMeasures}</span>
                </div>
              </div>
            )}

            {isOpen && !msds && (
              <div className={styles.msdsContent}>
                <div className={styles.noData}>
                  No MSDS data available for this material. Standard lab PPE recommended.
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
