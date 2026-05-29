import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import styles from "./Charts.module.css";

/**
 * Normalize property values to 0-100 scale for radar chart
 */
function normalize(value, max) {
  return Math.min(100, (value / max) * 100);
}

const PROPERTY_MAX = {
  heatResistance: 400,
  tensileStrength: 200,
  elongation: 500,
  ecoScore: 100,
  density: 2.5,
};

const PROPERTY_LABELS = {
  heatResistance: "Heat Res.",
  tensileStrength: "Tensile Str.",
  elongation: "Elongation",
  ecoScore: "Eco Score",
  density: "Density",
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: "rgba(10, 14, 39, 0.95)",
        border: "1px solid rgba(100, 120, 200, 0.3)",
        borderRadius: "8px",
        padding: "10px 14px",
        fontSize: "11px",
        fontFamily: "var(--font-mono)",
      }}>
        <div style={{ color: "#e8ecf4", fontWeight: 600, marginBottom: 4 }}>
          {payload[0]?.payload?.property}
        </div>
        {payload.map((p, i) => (
          <div key={i} style={{ color: p.color, marginTop: 2 }}>
            {p.name}: {p.payload[`raw_${p.dataKey}`] ?? p.value.toFixed(1)}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function PropertyRadar({ predicted, targets }) {
  if (!predicted) return null;

  const data = Object.keys(PROPERTY_LABELS).map((key) => {
    const item = {
      property: PROPERTY_LABELS[key],
      predicted: normalize(predicted[key] || 0, PROPERTY_MAX[key]),
      raw_predicted: predicted[key],
    };

    if (targets && targets[key] !== undefined) {
      item.target = normalize(targets[key], PROPERTY_MAX[key]);
      item.raw_target = targets[key];
    }

    return item;
  });

  return (
    <div className={`${styles.chartCard} glass-card`}>
      <div className={styles.chartTitle}>Property Analysis</div>
      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
            <PolarGrid stroke="rgba(100, 120, 200, 0.15)" />
            <PolarAngleAxis
              dataKey="property"
              tick={{ fill: "#8892b0", fontSize: 10, fontFamily: "var(--font-mono)" }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: "#5a6380", fontSize: 9 }}
              axisLine={false}
            />
            {targets && (
              <Radar
                name="Target"
                dataKey="target"
                stroke="#ff4081"
                fill="#ff4081"
                fillOpacity={0.1}
                strokeWidth={2}
                strokeDasharray="6 3"
                animationDuration={600}
              />
            )}
            <Radar
              name="Predicted"
              dataKey="predicted"
              stroke="#00ff88"
              fill="#00ff88"
              fillOpacity={0.15}
              strokeWidth={2}
              animationBegin={300}
              animationDuration={800}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span style={{ color: "#8892b0", fontSize: "11px" }}>{value}</span>
              )}
              iconType="line"
              iconSize={12}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
