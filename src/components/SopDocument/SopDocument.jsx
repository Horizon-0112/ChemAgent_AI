import ReactMarkdown from "react-markdown";
import styles from "./SopDocument.module.css";

export default function SopDocument({ content, title }) {
  if (!content) {
    return (
      <div className={styles.noContent}>
        Document will be generated after simulation completes.
      </div>
    );
  }

  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/\s+/g, "_").toLowerCase()}_${new Date().toISOString().split("T")[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.sopContainer}>
      <div className={styles.toolbar}>
        <span className={styles.toolbarTitle}>{title}</span>
        <button className={styles.downloadBtn} onClick={handleDownload}>
          ⬇ Download .md
        </button>
      </div>

      <div className={styles.documentFrame}>
        <div className={styles.markdownContent}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
