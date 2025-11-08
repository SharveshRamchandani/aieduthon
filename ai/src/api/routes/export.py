from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...exporters.ppt_exporter import PPTExporter


class ExportRequest(BaseModel):
	output_dir: str | None = None


router = APIRouter()


@router.post("/{deck_id}/export")
def export_deck(deck_id: str, body: ExportRequest):
	try:
		exporter = PPTExporter()
		path = exporter.export_deck(deck_id, body.output_dir or "..\\..\\out")
		return {"filePath": path}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


