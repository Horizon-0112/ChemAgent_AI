"""
Database connection — GCP Cloud SQL for PostgreSQL (Cloud Run 배포 전용).
Cloud SQL Python Connector를 통해 Unix socket으로 안전하게 연결합니다.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from google.cloud.sql.connector import AsyncConnector, IPTypes

from config import (
    CLOUD_SQL_CONNECTION_NAME,
    CLOUD_SQL_DATABASE,
    CLOUD_SQL_USER,
    CLOUD_SQL_PASSWORD,
)

_connector = AsyncConnector()


async def _getconn():
    """Cloud SQL Connector를 통한 비동기 연결 생성."""
    return await _connector.connect(
        CLOUD_SQL_CONNECTION_NAME,
        "asyncpg",
        user=CLOUD_SQL_USER,
        password=CLOUD_SQL_PASSWORD,
        db=CLOUD_SQL_DATABASE,
        ip_type=IPTypes.PUBLIC,  # VPC Connector 사용 시 IPTypes.PRIVATE 로 변경
    )


engine: AsyncEngine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",  # 더미 URL — Connector가 실제 연결 처리
    async_creator=_getconn,
    echo=False,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI 라우터 의존성 주입용."""
    async with async_session() as session:
        yield session


async def init_db():
    """모든 테이블을 생성합니다 (없는 경우에만)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
