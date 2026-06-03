"""
Dataset management API — CSV upload, list, and delete endpoints.
"""

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Dataset, Chemical, Catalyst, DEMO_DATASET_ID
from schemas.models import DatasetResponse, UploadResponse

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

# ── CSV column definitions ─────────────────────────────────────

CHEMICAL_REQUIRED = {"id", "name", "category", "heat_resistance", "tensile_strength", "eco_score", "hazard_level"}
CHEMICAL_OPTIONAL = {
    "name_ko", "sub_category", "molecular_weight", "elongation",
    "density", "cost_per_kg", "compatible_with", "color",
}
CHEMICAL_FLOAT_COLS = {"molecular_weight", "heat_resistance", "tensile_strength", "elongation", "eco_score", "density", "cost_per_kg"}

CATALYST_REQUIRED = {"id", "name", "type", "selectivity", "toxicity", "effect_on_strength", "effect_on_heat_res", "effect_on_eco"}
CATALYST_OPTIONAL = {
    "name_ko", "activation_temp", "lifetime", "cost_per_kg", "description",
}
CATALYST_FLOAT_COLS = {"activation_temp", "selectivity", "cost_per_kg", "effect_on_strength", "effect_on_heat_res", "effect_on_eco"}
CATALYST_INT_COLS = {"lifetime"}

VALID_HAZARD = {"low", "medium", "high"}
VALID_TOXICITY = {"low", "medium", "high"}


def _parse_chemical_csv(content: str, dataset_id: str) -> tuple[list, list, int]:
    """Parse CSV content into (list of Chemical objects, error list, skip count)."""
    reader = csv.DictReader(io.StringIO(content))
    headers = set(reader.fieldnames or [])

    missing = CHEMICAL_REQUIRED - headers
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(sorted(missing))}"
        )

    records, errors, skipped = [], [], 0

    for i, row in enumerate(reader, start=2):  # row 2 = first data row after header
        try:
            row_id = row.get("id", "").strip()
            row_name = row.get("name", "").strip()
            if not row_id or not row_name:
                errors.append(f"Row {i}: id or name is empty — skipped")
                skipped += 1
                continue

            # Validate hazard level
            hazard = row.get("hazard_level", "low").strip().lower()
            if hazard not in VALID_HAZARD:
                hazard = "low"

            # Convert numeric columns
            float_vals = {}
            for col in CHEMICAL_FLOAT_COLS:
                raw = row.get(col, "").strip()
                if raw:
                    try:
                        float_vals[col] = float(raw)
                    except ValueError:
                        errors.append(f"Row {i}, column '{col}': '{raw}' is not a number (set to 0)")
                        float_vals[col] = 0.0
                else:
                    float_vals[col] = None

            # compatible_with: comma-separated string → list
            compat_raw = row.get("compatible_with", "").strip()
            compatible_with = [x.strip() for x in compat_raw.split(",") if x.strip()] if compat_raw else []

            color = row.get("color", "#aaaaaa").strip() or "#aaaaaa"

            records.append(Chemical(
                id=row_id,
                name=row_name,
                name_ko=row.get("name_ko", "").strip() or None,
                category=row.get("category", "").strip(),
                sub_category=row.get("sub_category", "").strip() or None,
                hazard_level=hazard,
                color=color,
                compatible_with=compatible_with,
                dataset_id=dataset_id,
                **float_vals,
            ))
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
            skipped += 1

    return records, errors, skipped


def _parse_catalyst_csv(content: str, dataset_id: str) -> tuple[list, list, int]:
    """Parse CSV content into (list of Catalyst objects, error list, skip count)."""
    reader = csv.DictReader(io.StringIO(content))
    headers = set(reader.fieldnames or [])

    missing = CATALYST_REQUIRED - headers
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(sorted(missing))}"
        )

    records, errors, skipped = [], [], 0

    for i, row in enumerate(reader, start=2):
        try:
            row_id = row.get("id", "").strip()
            row_name = row.get("name", "").strip()
            if not row_id or not row_name:
                errors.append(f"Row {i}: id or name is empty — skipped")
                skipped += 1
                continue

            toxicity = row.get("toxicity", "low").strip().lower()
            if toxicity not in VALID_TOXICITY:
                toxicity = "low"

            float_vals = {}
            for col in CATALYST_FLOAT_COLS:
                raw = row.get(col, "").strip()
                if raw:
                    try:
                        float_vals[col] = float(raw)
                    except ValueError:
                        errors.append(f"Row {i}, column '{col}': '{raw}' is not a number (defaulting to 0)")
                        float_vals[col] = 0.0
                else:
                    float_vals[col] = None

            lifetime_raw = row.get("lifetime", "").strip()
            lifetime = int(float(lifetime_raw)) if lifetime_raw else None

            records.append(Catalyst(
                id=row_id,
                name=row_name,
                name_ko=row.get("name_ko", "").strip() or None,
                type=row.get("type", "").strip(),
                toxicity=toxicity,
                lifetime=lifetime,
                description=row.get("description", "").strip() or None,
                dataset_id=dataset_id,
                **float_vals,
            ))
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
            skipped += 1

    return records, errors, skipped


# ── API endpoints ───────────────────────────────────────────────────

@router.get("", response_model=List[DatasetResponse])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """List all datasets including the Demo Dataset."""
    result = await db.execute(select(Dataset).order_by(Dataset.created_at))
    return result.scalars().all()


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    name: str = Form(...),
    data_type: str = Form(...),  # "chemical" | "catalyst"
    description: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV file and save it as a new dataset."""
    if data_type not in ("chemical", "catalyst"):
        raise HTTPException(status_code=422, detail="data_type must be 'chemical' or 'catalyst'.")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Only CSV files are accepted.")

    raw = await file.read()
    try:
        content = raw.decode("utf-8-sig")  # Excel CSV with BOM support
    except UnicodeDecodeError:
        content = raw.decode("euc-kr", errors="replace")

    dataset_id = str(uuid.uuid4())

    if data_type == "chemical":
        records, errors, skipped = _parse_chemical_csv(content, dataset_id)
    else:
        records, errors, skipped = _parse_catalyst_csv(content, dataset_id)

    if not records:
        raise HTTPException(
            status_code=422,
            detail=f"No valid records found. Errors: {'; '.join(errors[:5])}"
        )

    dataset = Dataset(
        id=dataset_id,
        name=name,
        description=description,
        data_type=data_type,
        row_count=len(records),
        is_demo=False,
    )
    db.add(dataset)
    for rec in records:
        db.add(rec)

    await db.commit()

    return UploadResponse(
        dataset_id=dataset_id,
        name=name,
        row_count=len(records),
        skipped=skipped,
        errors=errors[:10],  # Return at most 10 errors
    )


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a dataset and all its associated records. The Demo Dataset cannot be deleted."""
    if dataset_id == DEMO_DATASET_ID:
        raise HTTPException(status_code=403, detail="The Demo Dataset cannot be deleted.")

    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if dataset.is_demo:
        raise HTTPException(status_code=403, detail="Built-in datasets cannot be deleted.")

    # Delete associated records
    if dataset.data_type == "chemical":
        await db.execute(delete(Chemical).where(Chemical.dataset_id == dataset_id))
    elif dataset.data_type == "catalyst":
        await db.execute(delete(Catalyst).where(Catalyst.dataset_id == dataset_id))

    await db.delete(dataset)
    await db.commit()

    return {"ok": True, "deleted": dataset_id}
