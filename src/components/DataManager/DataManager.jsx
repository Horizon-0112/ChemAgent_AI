import { useState, useEffect, useRef } from "react";
import styles from "./DataManager.module.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

export default function DataManager({ activeDatasetId, onActivate, onClose }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState("chemical");
  const [formDesc, setFormDesc] = useState("");
  const [pendingFile, setPendingFile] = useState(null);
  const fileInputRef = useRef(null);

  const fetchDatasets = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/datasets`);
      const data = await res.json();
      setDatasets(data);
    } catch {
      // keep existing
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileSelect = (file) => {
    if (!file || !file.name.endsWith(".csv")) {
      setUploadError("Only CSV files are supported.");
      return;
    }
    setUploadError("");
    setPendingFile(file);
    setFormName(file.name.replace(".csv", ""));
    setShowForm(true);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleUpload = async () => {
    if (!pendingFile || !formName.trim()) return;
    setUploading(true);
    setUploadError("");
    setUploadSuccess("");

    const fd = new FormData();
    fd.append("file", pendingFile);
    fd.append("name", formName.trim());
    fd.append("data_type", formType);
    fd.append("description", formDesc.trim());

    try {
      const res = await fetch(`${API_BASE}/api/datasets/upload`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      if (!res.ok) {
        setUploadError(data.detail || "Upload failed");
      } else {
        const warn = data.errors?.length > 0 ? ` (${data.skipped} rows skipped)` : "";
        setUploadSuccess(`✓ ${data.row_count} rows uploaded successfully${warn}`);
        setShowForm(false);
        setPendingFile(null);
        setFormName("");
        setFormDesc("");
        await fetchDatasets();
      }
    } catch {
      setUploadError("Server connection error");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (datasetId) => {
    if (!window.confirm("Delete this dataset? All associated records will be permanently removed.")) return;
    try {
      const res = await fetch(`${API_BASE}/api/datasets/${datasetId}`, { method: "DELETE" });
      if (res.ok) {
        if (activeDatasetId === datasetId) onActivate(null);
        await fetchDatasets();
      }
    } catch {
      // ignore
    }
  };

  const typeLabel = { chemical: "Chemical", catalyst: "Catalyst", demo: "Demo" };
  const typeColor = { chemical: styles.typeChem, catalyst: styles.typeCat, demo: styles.typeDemo };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerTitle}>
            <span className={styles.headerIcon}>🗄</span>
            Dataset Manager
          </div>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        {/* Upload Zone */}
        {!showForm ? (
          <div
            className={`${styles.dropZone} ${dragOver ? styles.dropZoneActive : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              style={{ display: "none" }}
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
            <div className={styles.dropIcon}>📂</div>
            <div className={styles.dropText}>Drag & drop a CSV file here, or click to browse</div>
            <div className={styles.dropSub}>Chemical or Catalyst data</div>
            <div className={styles.templateLinks}>
              <a href="/csv_template_chemical.csv" download onClick={(e) => e.stopPropagation()}>
                ↓ Chemical Template
              </a>
              <span>·</span>
              <a href="/csv_template_catalyst.csv" download onClick={(e) => e.stopPropagation()}>
                ↓ Catalyst Template
              </a>
            </div>
          </div>
        ) : (
          <div className={styles.uploadForm}>
            <div className={styles.formRow}>
              <label>Dataset Name</label>
              <input
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="My Experiment Data"
              />
            </div>
            <div className={styles.formRow}>
              <label>Data Type</label>
              <div className={styles.typeSelect}>
                {["chemical", "catalyst"].map((t) => (
                  <button
                    key={t}
                    className={`${styles.typeBtn} ${formType === t ? styles.typeBtnActive : ""}`}
                    onClick={() => setFormType(t)}
                  >
                    {t === "chemical" ? "⚗️ Chemical" : "🔬 Catalyst"}
                  </button>
                ))}
              </div>
            </div>
            <div className={styles.formRow}>
              <label>Description (optional)</label>
              <input
                value={formDesc}
                onChange={(e) => setFormDesc(e.target.value)}
                placeholder="e.g. experimental conditions, source"
              />
            </div>
            <div className={styles.selectedFile}>
              📄 {pendingFile?.name}
            </div>
            <div className={styles.formActions}>
              <button className={styles.cancelBtn} onClick={() => { setShowForm(false); setPendingFile(null); }}>
                Cancel
              </button>
              <button
                className={styles.uploadBtn}
                onClick={handleUpload}
                disabled={uploading || !formName.trim()}
              >
                {uploading ? "Uploading..." : "Upload"}
              </button>
            </div>
          </div>
        )}

        {uploadError && <div className={styles.errorMsg}>⚠ {uploadError}</div>}
        {uploadSuccess && <div className={styles.successMsg}>{uploadSuccess}</div>}

        {/* Dataset List */}
        <div className={styles.listSection}>
          <div className={styles.listTitle}>Datasets</div>
          {loading ? (
            <div className={styles.listEmpty}>Loading...</div>
          ) : datasets.length === 0 ? (
            <div className={styles.listEmpty}>No datasets found.</div>
          ) : (
            <div className={styles.list}>
              {datasets.map((ds) => {
                const isActive = activeDatasetId === ds.id || (!activeDatasetId && ds.is_demo);
                return (
                  <div key={ds.id} className={`${styles.item} ${isActive ? styles.itemActive : ""}`}>
                    <div className={styles.itemRadio}>
                      <span className={isActive ? styles.radioOn : styles.radioOff} />
                    </div>
                    <div className={styles.itemInfo}>
                      <div className={styles.itemName}>
                        {ds.name}
                        <span className={`${styles.typeTag} ${typeColor[ds.data_type] || ""}`}>
                          {typeLabel[ds.data_type] || ds.data_type}
                        </span>
                      </div>
                      <div className={styles.itemMeta}>
                        {ds.row_count} records · {new Date(ds.created_at).toLocaleDateString("en-US")}
                        {ds.description && <span> · {ds.description}</span>}
                      </div>
                    </div>
                    <div className={styles.itemActions}>
                      <button
                        className={`${styles.loadBtn} ${isActive ? styles.loadBtnActive : ""}`}
                        onClick={() => onActivate(ds.id)}
                        disabled={isActive}
                      >
                        {isActive ? "Active" : "Use"}
                      </button>
                      <button
                        className={styles.deleteBtn}
                        onClick={() => handleDelete(ds.id)}
                        disabled={ds.is_demo}
                        title={ds.is_demo ? "Built-in dataset cannot be deleted" : "Delete"}
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Active indicator */}
        <div className={styles.footer}>
          <span className={styles.footerLabel}>Active Dataset:</span>
          <span className={styles.footerValue}>
            {datasets.find((d) => d.id === activeDatasetId)?.name ||
              datasets.find((d) => d.is_demo)?.name ||
              "None"}
          </span>
        </div>
      </div>
    </div>
  );
}
