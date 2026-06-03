from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.connection import get_db
from database.models import Chemical, Catalyst, MsdsData
from schemas.models import ChemicalResponse, CatalystResponse, MsdsResponse

router = APIRouter(prefix="/api", tags=["Data"])


@router.get("/chemicals", response_model=List[ChemicalResponse])
async def get_chemicals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chemical))
    return result.scalars().all()


@router.get("/catalysts", response_model=List[CatalystResponse])
async def get_catalysts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Catalyst))
    return result.scalars().all()


@router.get("/msds", response_model=List[MsdsResponse])
async def get_all_msds(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MsdsData))
    return result.scalars().all()


@router.get("/msds/{chemical_id}", response_model=MsdsResponse)
async def get_msds(chemical_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MsdsData).where(MsdsData.chemical_id == chemical_id))
    return result.scalar_one_or_none()
