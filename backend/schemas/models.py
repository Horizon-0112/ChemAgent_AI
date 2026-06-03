from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SimulationParams(BaseModel):
    heatResistance: float
    tensileStrength: float
    ecoScore: float
    domain: str
    maxHazard: str
    datasetId: Optional[str] = None  # None이면 Demo Dataset 사용


class ChemicalResponse(BaseModel):
    id: str
    name: str
    category: str
    sub_category: str
    heat_resistance: float
    tensile_strength: float
    eco_score: float
    hazard_level: str
    color: str

    class Config:
        from_attributes = True


class CatalystResponse(BaseModel):
    id: str
    name: str
    type: str
    activation_temp: float
    selectivity: float
    toxicity: str
    effect_on_strength: float
    effect_on_heat_res: float
    effect_on_eco: float

    class Config:
        from_attributes = True


class MsdsResponse(BaseModel):
    chemical_id: str
    hazard_classification: str
    ghs_symbols: List[str]
    signal_word: str
    hazard_statements: List[str]
    precautionary_statements: List[str]
    first_aid: Dict[str, str]
    storage_conditions: str
    personal_protection: str
    emergency_measures: str

    class Config:
        from_attributes = True


class HistoryEntry(BaseModel):
    id: str
    created_at: str
    params: Dict[str, Any]
    formulation: List[Dict[str, Any]]
    predicted_properties: Dict[str, Any]
    catalyst_name: str
    catalyst_type: str
    score: float
    msds_warnings_count: int
    sop_document: str
    report_document: str


# ── Dataset 관련 스키마 ────────────────────────────────────────

class DatasetResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    data_type: str
    row_count: int
    is_demo: bool

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    dataset_id: str
    name: str
    row_count: int
    skipped: int
    errors: List[str]
