import { useState } from "react";
import useAgent from "./hooks/useAgentLocal.js";
import Header from "./components/Layout/Header.jsx";
import InputForm from "./components/InputForm/InputForm.jsx";
import AgentConsole from "./components/AgentConsole/AgentConsole.jsx";
import ResultDashboard from "./components/ResultDashboard/ResultDashboard.jsx";
import DataManager from "./components/DataManager/DataManager.jsx";
import styles from "./App.module.css";

export default function App() {
  const {
    status,
    logs,
    result,
    history,
    startAgent,
    resetAgent,
    loadFromHistory,
    clearHistory,
    deleteHistoryEntry,
    isRunning,
  } = useAgent();

  const [showHistory, setShowHistory] = useState(false);
  const [showDataManager, setShowDataManager] = useState(false);
  const [lastParams, setLastParams] = useState(null);
  const [activeDatasetId, setActiveDatasetId] = useState(null); // null = Demo Dataset

  const handleStart = (params) => {
    setLastParams(params);
    startAgent({ ...params, datasetId: activeDatasetId });
  };

  const handleReset = () => {
    resetAgent();
    setLastParams(null);
  };

  const handleLoadHistory = (entry) => {
    setLastParams(entry.params);
    loadFromHistory(entry);
    setShowHistory(false);
  };

  return (
    <div className={styles.app}>
      <Header
        status={status}
        historyCount={history.length}
        onToggleHistory={() => setShowHistory(true)}
        onToggleDataManager={() => setShowDataManager(true)}
        activeDatasetId={activeDatasetId}
      />

      <main className={styles.main}>
        {/* Left Panel — Input Form */}
        <div className={`${styles.panel} ${styles.panelLeft}`}>
          <InputForm
            onStart={handleStart}
            onReset={handleReset}
            isRunning={isRunning}
            status={status}
          />
        </div>

        {/* Center Panel — Agent Console */}
        <div className={`${styles.panel} ${styles.panelCenter}`}>
          <AgentConsole logs={logs} status={status} />
        </div>

        {/* Right Panel — Result Dashboard */}
        <div className={`${styles.panel} ${styles.panelRight}`}>
          <ResultDashboard result={result} params={lastParams} status={status} />
        </div>
      </main>

      {/* History Modal */}
      {showHistory && (
        <div className={styles.historyOverlay} onClick={() => setShowHistory(false)}>
          <div className={`${styles.historyPanel} glass-card`} onClick={(e) => e.stopPropagation()}>
            <div className={styles.historyHeader}>
              <span className={styles.historyTitle}>Simulation History</span>
              <div className={styles.historyActions}>
                {history.length > 0 && (
                  <button className={styles.historyClearBtn} onClick={clearHistory}>
                    Clear All
                  </button>
                )}
                <button className={styles.historyCloseBtn} onClick={() => setShowHistory(false)}>
                  ✕
                </button>
              </div>
            </div>

            <div className={styles.historyList}>
              {history.length === 0 ? (
                <div className={styles.historyEmpty}>
                  No simulation history yet. Run your first simulation to start building history.
                </div>
              ) : (
                history.map((entry) => (
                  <div
                    key={entry.id}
                    className={styles.historyItem}
                    onClick={() => handleLoadHistory(entry)}
                  >
                    <span className={styles.historyItemScore}>
                      {Math.round(entry.result.score)}
                    </span>
                    <div className={styles.historyItemInfo}>
                      <div className={styles.historyItemDomain}>
                        {entry.params.domain}
                      </div>
                      <div className={styles.historyItemMeta}>
                        Heat: {entry.params.heatResistance}°C · Strength: {entry.params.tensileStrength} MPa · Eco: {entry.params.ecoScore}
                      </div>
                    </div>
                    <span className={styles.historyItemDate}>
                      {new Date(entry.timestamp).toLocaleDateString()}
                    </span>
                    <button
                      className={styles.historyItemDelete}
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteHistoryEntry(entry.id);
                      }}
                      title="Delete entry"
                    >
                      🗑
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Dataset Manager Modal */}
      {showDataManager && (
        <DataManager
          activeDatasetId={activeDatasetId}
          onActivate={(id) => setActiveDatasetId(id)}
          onClose={() => setShowDataManager(false)}
        />
      )}
    </div>
  );
}
