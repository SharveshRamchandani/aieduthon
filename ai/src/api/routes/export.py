from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import os

from exporters.ppt_exporter import PPTExporter


class ExportRequest(BaseModel):
	output_dir: str | None = None


router = APIRouter()


@router.post("/{deck_id}/export")
def export_deck(deck_id: str, body: ExportRequest):
	"""Export deck and return file as downloadable response"""
	try:
		exporter = PPTExporter()
		# Default output directory relative to the ai/src directory
		if not body.output_dir:
			# Get the ai/src directory (3 levels up from routes/export.py)
			base_dir = Path(__file__).parent.parent.parent
			output_dir = str(base_dir / "out")
		else:
			output_dir = body.output_dir
		
		path = exporter.export_deck(deck_id, output_dir)
		
		# Return file as downloadable
		file_path = Path(path)
		if not file_path.exists():
			raise HTTPException(status_code=404, detail="Generated file not found")
		
		# Get filename for download
		filename = file_path.name
		
		return FileResponse(
			path=str(file_path),
			media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
			filename=filename,
			headers={"Content-Disposition": f'attachment; filename="{filename}"'}
		)
	except FileNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{deck_id}/download")
def download_deck(deck_id: str):
	"""Download an already exported deck"""
	try:
		from bson.objectid import ObjectId
		object_id = ObjectId(deck_id)
		
		# Find the file in the output directory
		out_dir = Path(__file__).parent.parent.parent / "out"
		filename = f"deck_{str(object_id)}.pptx"
		file_path = out_dir / filename
		
		if not file_path.exists():
			# Try to export it first
			exporter = PPTExporter()
			export_path = exporter.export_deck(deck_id, str(out_dir))
			file_path = Path(export_path)
		
		if not file_path.exists():
			raise HTTPException(status_code=404, detail="Deck file not found. Please export first.")
		
		return FileResponse(
			path=str(file_path),
			media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
			filename=filename,
			headers={"Content-Disposition": f'attachment; filename="{filename}"'}
		)
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


