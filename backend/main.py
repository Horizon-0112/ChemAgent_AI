from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import CORS_ORIGINS
from database.connection import init_db
from database.seed import seed_database
from routers import chemicals, simulation, history, export, datasets


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    await seed_database()
    print("Startup complete.")
    yield
    print("Shutting down...")


app = FastAPI(
    title="ChemAgent AI API",
    description="Backend API for autonomous R&D polymer formulation agent.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,      # 프로덕션에서 Swagger UI 비활성화
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chemicals.router)
app.include_router(simulation.router)
app.include_router(history.router)
app.include_router(export.router)
app.include_router(datasets.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "chemagent-api"}


# 프론트엔드 정적 파일 서빙 (빌드된 React 앱)
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
