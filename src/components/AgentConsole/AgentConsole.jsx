import { useEffect, useRef } from "react";
import styles from "./AgentConsole.module.css";

const PHASE_LABELS = {
  parsing: "Parsing inputs",
  scanning: "Scanning database",
  analyzing: "Compatibility analysis",
  safety: "MSDS safety review",
  optimizing: "Optimization engine",
  simulating: "Property simulation",
  documenting: "Document generation",
};

export default function AgentConsole({ logs, status }) {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const isRunning = !["idle", "complete", "error"].includes(status);

  return (
    <div className={styles.console}>
      <div className={styles.consoleHeader}>
        <div className={styles.consoleDots}>
          <span className={`${styles.consoleDot} ${styles.dotRed}`} />
          <span className={`${styles.consoleDot} ${styles.dotYellow}`} />
          <span className={`${styles.consoleDot} ${styles.dotGreen}`} />
        </div>
        <span className={styles.consoleTitle}>Agent Console</span>
        {isRunning && (
          <div className={styles.phaseIndicator}>
            <span className={styles.phaseSpinner} />
            {PHASE_LABELS[status] || status}
          </div>
        )}
      </div>

      <div className={styles.logArea} ref={scrollRef}>
        {logs.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>⟩_</div>
            <div className={styles.emptyText}>
              Agent console ready.<br />
              Configure parameters and press Start Design.
            </div>
          </div>
        ) : (
          <>
            {logs.map((log) => (
              <div
                key={log.id}
                className={`${styles.logLine} ${styles[`log${log.type}`] || ""}`}
              >
                {log.text}
              </div>
            ))}
            {isRunning && <span className={styles.cursor} />}
          </>
        )}
      </div>
    </div>
  );
}
