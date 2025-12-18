"""
TTS Routes: Endpoints for Text-to-Speech audio generation and download
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agents.tts_agent import TTSAgent

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateTTSRequest(BaseModel):
	"""Request model for generating TTS for a deck"""
	userId: str
	locale: str = "en"
	slow: bool = False


class GenerateTTSTextRequest(BaseModel):
	"""Request model for generating TTS from arbitrary text"""
	text: str = Field(min_length=1, max_length=5000)
	locale: str = "en"
	slow: bool = False
	output_filename: Optional[str] = None


@router.post("/slides/{deck_id}/tts")
def generate_tts_for_deck(deck_id: str, body: GenerateTTSRequest):
	"""
	Generate TTS audio for a slide deck
	
	Args:
		deck_id: ID of the slide deck
		body: TTS generation parameters
		
	Returns:
		Dict with audio files and metadata
	"""
	try:
		tts_agent = TTSAgent()
		result = tts_agent.generate_tts_for_deck(
			deck_id=deck_id,
			user_id=body.userId,
			locale=body.locale,
			slow=body.slow
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "TTS generation failed"))
		
		return result
		
	except Exception as e:
		logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/slides/{deck_id}/tts")
def get_tts_for_deck(deck_id: str):
	"""
	Get TTS audio metadata for a deck
	
	Args:
		deck_id: ID of the slide deck
		
	Returns:
		Dict with TTS metadata
	"""
	try:
		tts_agent = TTSAgent()
		tts_data = tts_agent.get_tts_for_deck(deck_id)
		
		if not tts_data:
			raise HTTPException(status_code=404, detail="TTS audio not found for this deck")
		
		# Convert ObjectId to string for JSON serialization
		tts_data["_id"] = str(tts_data["_id"])
		tts_data["deck_id"] = str(tts_data["deck_id"])
		
		return tts_data
		
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching TTS data: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts/{filename}")
def download_tts_file(filename: str):
	"""
	Download a TTS audio file
	
	Args:
		filename: Name of the audio file
		
	Returns:
		Audio file (MP3)
	"""
	try:
		# Security: Only allow .mp3 files
		if not filename.endswith('.mp3'):
			raise HTTPException(status_code=400, detail="Invalid file type")
		
		# Prevent path traversal
		if '..' in filename or '/' in filename or '\\' in filename:
			raise HTTPException(status_code=400, detail="Invalid filename")
		
		tts_agent = TTSAgent()
		file_path = Path(tts_agent.output_dir) / filename
		
		if not file_path.exists():
			raise HTTPException(status_code=404, detail="Audio file not found")
		
		return FileResponse(
			path=str(file_path),
			media_type="audio/mpeg",
			filename=filename
		)
		
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error serving TTS file: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-tts")
def generate_tts_from_text(body: GenerateTTSTextRequest):
	"""
	Generate TTS audio from arbitrary text
	
	Args:
		body: Text and TTS parameters
		
	Returns:
		Dict with audio file URL and metadata
	"""
	try:
		tts_agent = TTSAgent()
		result = tts_agent.generate_tts_for_text(
			text=body.text,
			locale=body.locale,
			slow=body.slow,
			output_filename=body.output_filename
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "TTS generation failed"))
		
		return result
		
	except Exception as e:
		logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))

