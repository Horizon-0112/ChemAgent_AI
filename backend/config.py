import os
from dotenv import load_dotenv

load_dotenv()

# ── Cloud SQL (GCP 배포) ──────────────────────────────────────
# 형식: "project-id:region:instance-name"
# 예시: "my-project:asia-northeast3:chemagent-db"
CLOUD_SQL_CONNECTION_NAME = os.environ["CLOUD_SQL_CONNECTION_NAME"]
CLOUD_SQL_DATABASE = os.getenv("CLOUD_SQL_DATABASE", "chemagent")
CLOUD_SQL_USER = os.getenv("CLOUD_SQL_USER", "chemagent_user")
CLOUD_SQL_PASSWORD = os.environ["CLOUD_SQL_PASSWORD"]

# ── Gemini API ────────────────────────────────────────────────
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── Server ────────────────────────────────────────────────────
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
