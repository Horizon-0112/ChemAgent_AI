import styles from "./Header.module.css";

const STATUS_MAP = {
  idle: { label: "STANDBY", className: styles.statusIdle },
  parsing: { label: "PARSING", className: styles.statusRunning },
  scanning: { label: "SCANNING DB", className: styles.statusRunning },
  analyzing: { label: "ANALYZING", className: styles.statusRunning },
  safety: { label: "MSDS REVIEW", className: styles.statusRunning },
  optimizing: { label: "OPTIMIZING", className: styles.statusRunning },
  simulating: { label: "SIMULATING", className: styles.statusRunning },
  documenting: { label: "GENERATING", className: styles.statusRunning },
  complete: { label: "COMPLETE", className: styles.statusComplete },
  error: { label: "ERROR", className: styles.statusError },
};

export default function Header({ status, historyCount, onToggleHistory }) {
  const s = STATUS_MAP[status] || STATUS_MAP.idle;

  return (
    <header className={styles.header}>
      <div className={styles.logoArea}>
        <div className={styles.logoIcon}>⚗️</div>
        <div className={styles.logoText}>
          <span className={styles.logoTitle}>ChemAgent AI</span>
          <span className={styles.logoSub}>Autonomous R&D Formulation Engine</span>
        </div>
      </div>

      <div className={styles.statusArea}>
        <div className={`${styles.statusBadge} ${s.className}`}>
          <span className={styles.statusDot} />
          {s.label}
        </div>

        {historyCount > 0 && (
          <button
            className={styles.historyBtn}
            onClick={onToggleHistory}
            title="View simulation history"
          >
            📋 History
            <span className={styles.historyCount}>{historyCount}</span>
          </button>
        )}
      </div>
    </header>
  );
}
