import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import styles from "./Charts.module.css";

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0];
    return (
      <div style={{
        background: "rgba(10, 14, 39, 0.95)",
        border: "1px solid rgba(100, 120, 200, 0.3)",
        borderRadius: "8px",
        padding: "10px 14px",
        fontSize: "12px",
        fontFamily: "var(--font-mono)",
      }}>
        <div style={{ color: d.payload.color, fontWeight: 600, marginBottom: 4 }}>
          {d.name}
        </div>
        <div style={{ color: "#e8ecf4" }}>
          {d.value.toFixed(1)}%
        </div>
      </div>
    );
  }
  return null;
};

const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.08) return null;
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central"
      style={{ fontSize: "11px", fontWeight: 600, fontFamily: "var(--font-mono)" }}>
      {(percent * 100).toFixed(0)}%
    </text>
  );
};

export default function CompositionChart({ formulation }) {
  if (!formulation || formulation.length === 0) return null;

  const data = formulation.map((f) => ({
    name: f.name,
    value: f.ratio,
    color: f.color,
  }));

  return (
    <div className={`${styles.chartCard} glass-card`}>
      <div className={styles.chartTitle}>Formulation Composition</div>
      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={95}
              paddingAngle={3}
              dataKey="value"
              labelLine={false}
              label={renderCustomLabel}
              animationBegin={200}
              animationDuration={800}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} stroke="rgba(0,0,0,0.3)" strokeWidth={1} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span style={{ color: "#8892b0", fontSize: "11px" }}>{value}</span>
              )}
              iconType="circle"
              iconSize={8}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
