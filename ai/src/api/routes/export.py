from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import os
import logging
import base64
import io
import zipfile

from exporters.ppt_exporter import PPTExporter
from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class ExportRequest(BaseModel):
	output_dir: str | None = None
	format: str = "pptx"  # "pptx" or "pdf"
	user_name: str = "user"  # User name for filename
	export_style: str = "template"  # "template" or "preview"


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
			format_type=body.format,
			export_style=body.export_style or "template",
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

		# 1) Try to serve directly from DB (preferred)
		db = get_ai_db()
		slides = db["slides"]
		doc = slides.find_one({"_id": object_id}, {"ppt_file": 1, "ppt_filename": 1})
		if doc and doc.get("ppt_file"):
			try:
				ppt_bytes = base64.b64decode(doc["ppt_file"])
				filename = doc.get("ppt_filename") or f"deck_{str(object_id)}.pptx"
				return Response(
					content=ppt_bytes,
					media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
					headers={
						"Content-Disposition": f'attachment; filename="{filename}"',
						"Content-Length": str(len(ppt_bytes))
					}
				)
			except Exception as decode_err:
				logger.error(f"Failed to decode PPT from DB for deck {deck_id}: {decode_err}")
				# Fall through to regeneration

		# 2) Regenerate and persist to DB if missing
		exporter = PPTExporter()
		ppt_bytes, filename = exporter.export_deck_to_bytes(deck_id, save_to_db=True)
		if ppt_bytes:
			return Response(
				content=ppt_bytes,
				media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
				headers={
					"Content-Disposition": f'attachment; filename="{filename}"',
					"Content-Length": str(len(ppt_bytes))
				}
			)

		# 3) Final fallback to legacy filesystem path (backward compatibility)
		out_dir = Path(__file__).parent.parent.parent / "out"
		filename = f"deck_{str(object_id)}.pptx"
		file_path = out_dir / filename
		if file_path.exists():
			return FileResponse(
				path=str(file_path),
				media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
				filename=filename,
				headers={"Content-Disposition": f'attachment; filename="{filename}"'}
			)

		raise HTTPException(status_code=404, detail="Deck file not found. Please export first.")
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{deck_id}/images-zip")
def download_deck_images(deck_id: str):
	"""Download all locally stored images/diagrams for a deck as a ZIP file."""
	try:
		from bson.objectid import ObjectId

		db = get_ai_db()
		slides = db["slides"]
		deck = slides.find_one({"_id": ObjectId(deck_id)}, {"title": 1, "media_refs": 1, "diagram_refs": 1})
		if not deck:
			raise HTTPException(status_code=404, detail="Deck not found")

		media_refs = deck.get("media_refs") or []
		diagram_refs = deck.get("diagram_refs") or []

		# Collect unique local file paths
		image_paths: list[Path] = []

		def add_path_from_ref(ref: str):
			if not ref:
				return
			# Generated images served from /media -> out/generated_images
			if ref.startswith("/media/"):
				filename = Path(ref).name
				path = Path("out/generated_images") / filename
			# Diagrams stored as filesystem paths like out/generated_diagrams/xxx.png
			elif ref.startswith("out/generated_diagrams"):
				path = Path(ref)
			# Anything else (remote URLs, unknown schemes) is skipped
			else:
				return

			if path.exists() and path.is_file():
				if path not in image_paths:
					image_paths.append(path)

		for slide_media in media_refs:
			for ref in slide_media or []:
				if isinstance(ref, str):
					add_path_from_ref(ref)

		for slide_diagrams in diagram_refs:
			for ref in slide_diagrams or []:
				if isinstance(ref, str):
					add_path_from_ref(ref)

		if not image_paths:
			raise HTTPException(status_code=404, detail="No downloadable images found for this deck")

		# Build ZIP in memory
		buffer = io.BytesIO()
		with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
			for idx, path in enumerate(image_paths, start=1):
				arcname = f"image_{idx}{path.suffix}"
				zf.write(path, arcname=arcname)

		buffer.seek(0)

		title = deck.get("title") or f"deck_{deck_id}"
		safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")[:50]
		filename = f"{safe_title or 'deck'}_images.zip"

		return StreamingResponse(
			buffer,
			media_type="application/zip",
			headers={
				"Content-Disposition": f'attachment; filename="{filename}"'
			},
		)
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Failed to build images ZIP for deck {deck_id}: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Failed to download deck images: {str(e)}")


