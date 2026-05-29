import { useState, useCallback, useEffect } from "react";
import { runAgentPipeline } from "../engine/agentEngine.js";

const HISTORY_KEY = "chemagent_history";

export default function useAgentLocal() {
  const [status, setStatus] = useState("idle"); // idle | running | complete | error
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(HISTORY_KEY);
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  }, []);

  const saveHistory = (newEntry) => {
    setHistory((prev) => {
      const updated = [newEntry, ...prev].slice(0, 20); // Keep last 20
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const startAgent = useCallback(async (params) => {
    setStatus("running");
    setIsRunning(true);
    setLogs([]);
    setResult(null);

    try {
      const finalResult = await runAgentPipeline(
        params,
        (logEntry) => {
          setLogs((prev) => [...prev, logEntry]);
        },
        (phase) => {
          // You can handle phase changes here if needed
          console.log("Phase changed:", phase);
        }
      );

      setResult(finalResult);
      setStatus("complete");
      setIsRunning(false);

      // Create history entry
      const historyEntry = {
        id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        params,
        result: finalResult,
      };
      saveHistory(historyEntry);

    } catch (error) {
      console.error(error);
      setLogs((prev) => [...prev, { type: "ERROR", text: `[Error] ${error.message}` }]);
      setStatus("error");
      setIsRunning(false);
    }
  }, []);

  const resetAgent = useCallback(() => {
    setStatus("idle");
    setLogs([]);
    setResult(null);
    setIsRunning(false);
  }, []);

  const loadFromHistory = useCallback((entry) => {
    setStatus("complete");
    setResult(entry.result);
    setLogs([{ type: "SYSTEM", text: `[System] Loaded history record from ${new Date(entry.timestamp).toLocaleString()}` }]);
  }, []);

  const clearHistory = useCallback(() => {
    localStorage.removeItem(HISTORY_KEY);
    setHistory([]);
  }, []);

  const deleteHistoryEntry = useCallback((id) => {
    setHistory((prev) => {
      const updated = prev.filter((item) => item.id !== id);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  return {
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
  };
}
