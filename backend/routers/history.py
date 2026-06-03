from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.connection import get_db
from database.models import Simulation
from schemas.models import HistoryEntry

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=List[HistoryEntry])
async def get_history(db: AsyncSession = Depends(get_db)):
    """Fetch all past simulations, ordered by newest first."""
    result = await db.execute(select(Simulation).order_by(Simulation.created_at.desc()).limit(20))
    simulations = result.scalars().all()
    
    history_entries = []
    for s in simulations:
        history_entries.append(HistoryEntry(
            id=str(s.id),
            created_at=s.created_at.isoformat(),
            params=s.params,
            formulation=s.formulation,
            predicted_properties=s.predicted_properties,
            catalyst_name=s.catalyst_name,
            catalyst_type=s.catalyst_type,
            score=s.score,
            msds_warnings_count=s.msds_warnings_count,
            sop_document=s.sop_document,
            report_document=s.report_document
        ))
    
    return history_entries


@router.delete("/{sim_id}")
async def delete_history(sim_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a specific simulation from history."""
    await db.execute(delete(Simulation).where(Simulation.id == sim_id))
    await db.commit()
    return {"status": "success"}


@router.delete("")
async def clear_history(db: AsyncSession = Depends(get_db)):
    """Clear all simulation history."""
    await db.execute(delete(Simulation))
    await db.commit()
    return {"status": "success"}
