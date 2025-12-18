"""
TTS Agent: Generates Text-to-Speech audio for presentations
Uses Google TTS (gTTS) for high-quality speech synthesis
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
	from gtts import gTTS
except ImportError:
	gTTS = None
	logging.warning("gTTS not installed. TTS functionality will be disabled.")

from ai_db import get_ai_db
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)


class TTSAgent:
	"""Agent that generates Text-to-Speech audio for slide presentations"""
	
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]
		self.tts_collection = self.db["tts_audio"]
		
		# Create output directory for TTS files
		self.output_dir = Path("out/tts_audio")
		self.output_dir.mkdir(parents=True, exist_ok=True)
		
		if gTTS is None:
			logger.warning("gTTS library not available. TTS generation will fail.")
	
	def generate_tts_for_deck(self,
							deck_id: str,
							user_id: str,
							locale: str = "en",
							slow: bool = False) -> Dict[str, Any]:
		"""
		Generate TTS audio for entire slide deck
		
		Args:
			deck_id: ID of the slide deck
			user_id: User identifier
			locale: Language code (en, hi, ta, etc.)
			slow: Whether to use slow speech (default: False)
			
		Returns:
			Dict with generated audio files and metadata
		"""
		if gTTS is None:
			return {
				"success": False,
				"error": "gTTS library not installed. Please install: pip install gtts"
			}
		
		try:
			# Get slide deck
			deck = self._get_slide_deck(deck_id)
			if not deck:
				return {"success": False, "error": "Slide deck not found"}
			
			# Generate audio for each slide
			audio_files = []
			slides = deck.get("sections", [])
			bullets = deck.get("bullets", [])
			
			for i, (section, slide_bullets) in enumerate(zip(slides, bullets)):
				# Combine slide title and content
				text = self._prepare_text_for_tts(section, slide_bullets)
				
				# Generate audio for this slide
				audio_result = self._generate_audio(text, locale, slow, deck_id, i)
				if audio_result.get("success"):
					audio_files.append(audio_result)
			
			# Generate combined audio for entire presentation
			all_text = "\n\n".join([
				self._prepare_text_for_tts(section, slide_bullets)
				for section, slide_bullets in zip(slides, bullets)
			])
			combined_audio = self._generate_audio(
				all_text, locale, slow, deck_id, "combined"
			)
			
			# Store TTS metadata in database
			tts_doc = {
				"deck_id": ObjectId(deck_id),
				"user_id": user_id,
				"locale": locale,
				"generated_at": datetime.utcnow(),
				"audio_files": [
					{
						"slide_index": audio.get("slide_index"),
						"file_path": audio.get("file_path"),
						"file_url": audio.get("file_url"),
						"duration_estimate": audio.get("duration_estimate")
					}
					for audio in audio_files
				],
				"combined_audio": {
					"file_path": combined_audio.get("file_path"),
					"file_url": combined_audio.get("file_url"),
					"duration_estimate": combined_audio.get("duration_estimate")
				} if combined_audio.get("success") else None
			}
			
			self.tts_collection.insert_one(tts_doc)
			
			return {
				"success": True,
				"audio_files": audio_files,
				"combined_audio": combined_audio if combined_audio.get("success") else None,
				"metadata": {
					"generated_at": datetime.utcnow(),
					"deck_id": deck_id,
					"total_slides": len(audio_files),
					"locale": locale
				}
			}
			
		except Exception as e:
			logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
			return {
				"success": False,
				"error": str(e),
				"audio_files": []
			}
	
	def generate_tts_for_text(self,
							 text: str,
							 locale: str = "en",
							 slow: bool = False,
							 output_filename: Optional[str] = None) -> Dict[str, Any]:
		"""
		Generate TTS audio for arbitrary text
		
		Args:
			text: Text to convert to speech
			locale: Language code (en, hi, ta, etc.)
			slow: Whether to use slow speech
			output_filename: Optional custom filename
			
		Returns:
			Dict with audio file path and metadata
		"""
		if gTTS is None:
			return {
				"success": False,
				"error": "gTTS library not installed"
			}
		
		try:
			return self._generate_audio(text, locale, slow, None, None, output_filename)
		except Exception as e:
			logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
			return {
				"success": False,
				"error": str(e)
			}
	
	def _generate_audio(self,
					   text: str,
					   locale: str,
					   slow: bool,
					   deck_id: Optional[str] = None,
					   slide_index: Optional[Any] = None,
					   output_filename: Optional[str] = None) -> Dict[str, Any]:
		"""Generate audio file from text using gTTS"""
		try:
			# Create gTTS object
			tts = gTTS(text=text, lang=locale, slow=slow)
			
			# Generate filename
			if output_filename:
				filename = output_filename
			elif deck_id and slide_index is not None:
				filename = f"deck_{deck_id}_slide_{slide_index}.mp3"
			elif deck_id:
				filename = f"deck_{deck_id}_combined.mp3"
			else:
				filename = f"tts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
			
			# Ensure .mp3 extension
			if not filename.endswith('.mp3'):
				filename += '.mp3'
			
			# Save to file
			file_path = self.output_dir / filename
			tts.save(str(file_path))
			
			# Calculate estimated duration (rough estimate: ~150 words per minute)
			word_count = len(text.split())
			duration_estimate = (word_count / 150) * 60  # seconds
			
			# Create URL path (relative to media serving)
			file_url = f"/tts/{filename}"
			
			return {
				"success": True,
				"file_path": str(file_path),
				"file_url": file_url,
				"filename": filename,
				"slide_index": slide_index,
				"duration_estimate": round(duration_estimate, 2),
				"word_count": word_count
			}
			
		except Exception as e:
			logger.error(f"Audio generation failed: {str(e)}", exc_info=True)
			return {
				"success": False,
				"error": str(e)
			}
	
	def _prepare_text_for_tts(self, section: str, bullets: List[str]) -> str:
		"""Prepare slide content for TTS by combining title and bullets"""
		text_parts = [section]  # Start with slide title
		
		# Add bullets
		for bullet in bullets:
			if bullet.strip():
				text_parts.append(bullet.strip())
		
		return ". ".join(text_parts) + "."
	
	def _get_slide_deck(self, deck_id: str) -> Optional[Dict]:
		"""Get slide deck from database"""
		try:
			deck = self.slides_collection.find_one({"_id": ObjectId(deck_id)})
			return deck
		except Exception as e:
			logger.error(f"Error fetching slide deck: {str(e)}")
			return None
	
	def get_tts_for_deck(self, deck_id: str) -> Optional[Dict]:
		"""Get TTS audio metadata for a deck"""
		try:
			tts_doc = self.tts_collection.find_one({"deck_id": ObjectId(deck_id)})
			return tts_doc
		except Exception as e:
			logger.error(f"Error fetching TTS data: {str(e)}")
			return None

