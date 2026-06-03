import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from database.connection import async_session
from services.agent_engine import run_agent_stream
from schemas.models import SimulationParams

router = APIRouter(prefix="/api/simulate", tags=["Simulation"])


@router.post("")
async def start_simulation(params: SimulationParams, request: Request):
    """
    Start the agent simulation pipeline and stream logs back to the client using SSE.
    """
    
    async def event_generator():
        try:
            # We use a new session inside the generator
            async with async_session() as session:
                async for event in run_agent_stream(params.model_dump(), session):
                    # Check if client disconnected
                    if await request.is_disconnected():
                        print("Client disconnected.")
                        break
                    yield event
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
