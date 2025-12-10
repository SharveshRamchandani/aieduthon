from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from pathlib import Path
import os
import logging

from exporters.ppt_exporter import PPTExporter

logger = logging.getLogger(__name__)


class ExportRequest(BaseModel):
	output_dir: str | None = None
	format: str = "pptx"  # "pptx" or "pdf"
	user_name: str = "user"  # User name for filename


router = APIRouter()


@router.post("/{deck_id}/export")
def export_deck(deck_id: str, body: ExportRequest):
	"""Export deck and return file as downloadable response"""
	try:
		exporter = PPTExporter()
		
		# Export to bytes (supports both PPTX and PDF)
		file_bytes, filename = exporter.export_deck_to_bytes(
			deck_id, 
			save_to_db=(body.format == "pptx"),  # Only save PPTX to DB for now
			user_name=body.user_name,
			format_type=body.format
		)
		
		# Determine media type
		if body.format == "pdf":
			media_type = "application/pdf"
		else:
			media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
		
		return Response(
			content=file_bytes,
			media_type=media_type,
			headers={
				"Content-Disposition": f'attachment; filename="{filename}"',
				"Content-Length": str(len(file_bytes))
			}
		)
	except ValueError as e:
		# Invalid deck_id format (not a valid ObjectId)
		logger.error(f"Invalid deck_id format for export: {deck_id}, error: {str(e)}")
		raise HTTPException(status_code=400, detail=f"Invalid deck ID format: {str(e)}")
	except FileNotFoundError as e:
		# Deck not found in database
		logger.error(f"Deck not found for export: {deck_id}, error: {str(e)}")
		raise HTTPException(status_code=404, detail=str(e))
	except RuntimeError as e:
		logger.error(f"Runtime error during export for deck {deck_id}: {str(e)}")
		raise HTTPException(status_code=500, detail=str(e))
	except ImportError as e:
		logger.error(f"Import error during PDF export for deck {deck_id}: {str(e)}")
		raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")
	except Exception as e:
		# Catch-all for any other exceptions - log the full error for debugging
		logger.error(f"Unexpected error during export for deck {deck_id}: {type(e).__name__}: {str(e)}", exc_info=True)
		raise HTTPException(status_code=400, detail=f"Export failed: {type(e).__name__}: {str(e)}")


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


