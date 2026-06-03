"""
SQLAlchemy ORM models for the ChemAgent database.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, Boolean
from database.connection import Base

# 고정 ID — Demo Dataset (seed 데이터용)
DEMO_DATASET_ID = "demo-dataset-00"


class Dataset(Base):
    """업로드된 CSV 데이터셋 메타데이터."""
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    data_type = Column(String(20), nullable=False)  # "chemical" | "catalyst" | "demo"
    row_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=False)  # Demo Dataset은 삭제 불가


class Chemical(Base):
    __tablename__ = "chemicals"

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    name_ko = Column(String(100))
    category = Column(String(50))
    sub_category = Column(String(50))
    molecular_weight = Column(Float)
    heat_resistance = Column(Float)
    tensile_strength = Column(Float)
    elongation = Column(Float)
    eco_score = Column(Float)
    density = Column(Float)
    hazard_level = Column(String(10))
    cost_per_kg = Column(Float)
    compatible_with = Column(JSON)  # List of catalyst IDs
    color = Column(String(10))
    # 데이터셋 소속: NULL이면 구형 seed, 값이 있으면 해당 Dataset 소속
    dataset_id = Column(String(36), nullable=True, index=True)


class Catalyst(Base):
    __tablename__ = "catalysts"

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    name_ko = Column(String(100))
    type = Column(String(50))
    activation_temp = Column(Float)
    selectivity = Column(Float)
    toxicity = Column(String(10))
    lifetime = Column(Integer)
    cost_per_kg = Column(Float)
    effect_on_strength = Column(Float)
    effect_on_heat_res = Column(Float)
    effect_on_eco = Column(Float)
    description = Column(Text)
    # 데이터셋 소속
    dataset_id = Column(String(36), nullable=True, index=True)


class MsdsData(Base):
    __tablename__ = "msds_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chemical_id = Column(String(10), nullable=False)
    hazard_classification = Column(String(50))
    ghs_symbols = Column(JSON)
    signal_word = Column(String(20))
    hazard_statements = Column(JSON)
    precautionary_statements = Column(JSON)
    first_aid = Column(JSON)
    storage_conditions = Column(Text)
    disposal_method = Column(Text)
    personal_protection = Column(Text)
    emergency_measures = Column(Text)


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    params = Column(JSON)
    formulation = Column(JSON)
    predicted_properties = Column(JSON)
    catalyst_name = Column(String(100))
    catalyst_type = Column(String(50))
    score = Column(Float)
    msds_warnings_count = Column(Integer, default=0)
    sop_document = Column(Text)
    report_document = Column(Text)
