from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.export_service import markdown_to_docx

router = APIRouter(prefix="/api/export", tags=["export"])

class ExportRequest(BaseModel):
    markdown: str
    title: str = "Document"

@router.post("/docx")
async def export_to_docx(req: ExportRequest):
    try:
        file_stream = markdown_to_docx(req.markdown)
        
        # Clean up title for filename
        safe_title = "".join([c for c in req.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"{safe_title.replace(' ', '_')}.docx"
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        print(f"Export error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export document")
