import { useState } from "react";
import styles from "./InputForm.module.css";

const DOMAINS = [
  "Automotive",
  "Electronics",
  "Packaging",
  "Construction",
  "Aerospace",
  "Medical",
  "Consumer Goods",
  "Energy",
];

export default function InputForm({ onStart, onReset, isRunning, status }) {
  const [formData, setFormData] = useState({
    heatResistance: 250,
    tensileStrength: 70,
    ecoScore: 60,
    domain: "Automotive",
    maxHazard: "medium",
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onStart(formData);
  };

  const showReset = status === "complete" || status === "error";

  return (
    <form className={styles.formContainer} onSubmit={handleSubmit}>
      <div className={styles.sectionTitle}>Target Properties</div>

      <div className={styles.formGrid}>
        {/* Heat Resistance */}
        <div className={styles.fieldGroup}>
          <div className={styles.sliderHeader}>
            <label>Heat Resistance</label>
            <span className={styles.sliderValue}>{formData.heatResistance}°C</span>
          </div>
          <input
            type="range"
            className={styles.slider}
            min={80}
            max={400}
            step={5}
            value={formData.heatResistance}
            onChange={(e) => handleChange("heatResistance", Number(e.target.value))}
            disabled={isRunning}
          />
        </div>

        {/* Tensile Strength */}
        <div className={styles.fieldGroup}>
          <div className={styles.sliderHeader}>
            <label>Tensile Strength</label>
            <span className={styles.sliderValue}>{formData.tensileStrength} MPa</span>
          </div>
          <input
            type="range"
            className={styles.slider}
            min={20}
            max={200}
            step={5}
            value={formData.tensileStrength}
            onChange={(e) => handleChange("tensileStrength", Number(e.target.value))}
            disabled={isRunning}
          />
        </div>

        {/* Eco Score */}
        <div className={styles.fieldGroup}>
          <div className={styles.sliderHeader}>
            <label>Min Eco Score</label>
            <span className={styles.sliderValue}>{formData.ecoScore}/100</span>
          </div>
          <input
            type="range"
            className={styles.slider}
            min={10}
            max={100}
            step={5}
            value={formData.ecoScore}
            onChange={(e) => handleChange("ecoScore", Number(e.target.value))}
            disabled={isRunning}
          />
        </div>

        {/* Domain */}
        <div className={styles.fieldGroup}>
          <label>Application Domain</label>
          <select
            value={formData.domain}
            onChange={(e) => handleChange("domain", e.target.value)}
            disabled={isRunning}
          >
            {DOMAINS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {/* Hazard Level */}
        <div className={`${styles.fieldGroup} ${styles.fieldGroupFull}`}>
          <label>Max Hazard Level</label>
          <div className={styles.hazardOptions}>
            {["low", "medium", "high"].map((level) => (
              <button
                key={level}
                type="button"
                className={`${styles.hazardOption} ${formData.maxHazard === level ? styles.hazardOptionActive : ""}`}
                onClick={() => handleChange("maxHazard", level)}
                disabled={isRunning}
              >
                <span className={`${styles.hazardDot} ${
                  level === "low" ? styles.hazardLow : level === "medium" ? styles.hazardMedium : styles.hazardHigh
                }`} />
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {showReset ? (
        <button
          type="button"
          className={styles.resetBtn}
          onClick={onReset}
        >
          ↻ New Simulation
        </button>
      ) : (
        <button
          type="submit"
          className={`${styles.startBtn} ${isRunning ? styles.startBtnRunning : ""}`}
          disabled={isRunning}
        >
          {isRunning ? "⟳ Agent Running..." : "🚀 Start Design"}
        </button>
      )}
    </form>
  );
}
