import { useState, useCallback, useEffect, useRef } from "react";
import { apiClient } from "../api/client.js";

export default function useAgent() {
  const [status, setStatus] = useState("idle"); // idle | running | complete | error
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const sseRef = useRef(null);

  // Load history from DB on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await apiClient.getHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const startAgent = useCallback((params) => {
    // Reset state
    setStatus("running");
    setLogs([{ type: "SYSTEM", text: `[${new Date().toLocaleTimeString()}] ▶ Initializing connection to AI core...` }]);
    setResult(null);

    // Close previous SSE connection if any
    if (sseRef.current) {
      sseRef.current.close();
    }

    // Start SSE request using fetch to send POST payload, then read stream
    const startStream = async () => {
      try {
        const response = await fetch('/api/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params),
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          
          // Parse SSE format
          const lines = buffer.split('\n\n');
          buffer = lines.pop(); // Keep incomplete chunk in buffer

          for (const chunk of lines) {
            const eventMatch = chunk.match(/event: (.*)/);
            const dataMatch = chunk.match(/data: (.*)/);

            if (eventMatch && dataMatch) {
              const eventName = eventMatch[1].trim();
              const eventData = JSON.parse(dataMatch[1].trim());

              if (eventName === 'log') {
                setLogs((prev) => [...prev, eventData]);
              } else if (eventName === 'result') {
                setResult(eventData);
                setStatus("complete");
                fetchHistory(); // Refresh history
              } else if (eventName === 'error') {
                setLogs((prev) => [...prev, { type: "ERROR", text: `[Error] ${eventData.error}` }]);
                setStatus("error");
              }
            }
          }
        }
      } catch (error) {
        console.error("Stream error:", error);
        setLogs((prev) => [...prev, { type: "ERROR", text: `[Connection Error] ${error.message}` }]);
        setStatus("error");
      }
    };

    startStream();
  }, []);

  const resetAgent = useCallback(() => {
    if (sseRef.current) {
      sseRef.current.close();
      sseRef.current = null;
    }
    setStatus("idle");
    setLogs([]);
    setResult(null);
  }, []);

  const loadFromHistory = useCallback((entry) => {
    setStatus("complete");
    setResult({
      formulation: entry.formulation,
      predictedProperties: entry.predicted_properties,
      selectedCatalyst: {
        name: entry.catalyst_name,
        type: entry.catalyst_type
      },
      score: entry.score,
      msdsWarnings: [], // Omitted for brevity in history load
      sopDocument: entry.sop_document,
      reportDocument: entry.report_document
    });
    setLogs([{ type: "SYSTEM", text: `[System] Loaded history record from ${new Date(entry.created_at).toLocaleString()}` }]);
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      await apiClient.clearHistory();
      setHistory([]);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const deleteHistoryEntry = useCallback(async (id) => {
    try {
      await apiClient.deleteHistoryEntry(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error(err);
    }
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
    isRunning: status === "running",
  };
}
