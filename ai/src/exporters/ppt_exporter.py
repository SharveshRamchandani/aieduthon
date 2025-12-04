from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from bson.objectid import ObjectId
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from ai_db import get_ai_db


class PPTExporter:
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]

	def export_deck(self, deck_id: str, output_dir: str = "..\\..\\out") -> str:
		"""Export slide deck to disk (legacy behavior)."""
		prs, fname = self._build_presentation(deck_id)
		out_dir = Path(output_dir).resolve()
		out_dir.mkdir(parents=True, exist_ok=True)
		output_path = out_dir / fname
		prs.save(str(output_path))
		return str(output_path)

	def export_deck_to_bytes(self, deck_id: str) -> Tuple[bytes, str]:
		"""Return PPTX content as bytes plus suggested filename."""
		prs, fname = self._build_presentation(deck_id)
		buffer = BytesIO()
		prs.save(buffer)
		return buffer.getvalue(), fname

	def _build_presentation(self, deck_id: str) -> Tuple[Presentation, str]:
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			raise ValueError("Invalid deck_id. Must be a Mongo ObjectId hex string.")

		deck = self.slides_collection.find_one({"_id": object_id})
		if not deck:
			raise FileNotFoundError("Slide deck not found")

		template_path = deck.get("template_path") or deck.get("metadata", {}).get("template_path")
		if template_path and Path(template_path).exists():
			prs = Presentation(template_path)
		else:
			prs = Presentation()

		# Title slide – overwrite the first slide in the template if present,
		# otherwise add a new one using the title layout.
		if len(prs.slides):
			slide = prs.slides[0]
			title_shape = getattr(slide.shapes, "title", None)
			if title_shape is not None:
				title_shape.text = deck.get("title", "AI Presentation")
			else:
				# Fallback textbox if template has no explicit title shape
				box = slide.shapes.add_textbox(Inches(1.0), Inches(0.5), Inches(8.0), Inches(1.5))
				box.text = deck.get("title", "AI Presentation")
			try:
				subtitle = slide.placeholders[1]
				subtitle.text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
			except Exception:
				# Not all templates have a subtitle placeholder; ignore.
				pass
		else:
			title_layout = prs.slide_layouts[0]
			slide = prs.slides.add_slide(title_layout)
			if slide.shapes.title:
				slide.shapes.title.text = deck.get("title", "AI Presentation")
			try:
				subtitle = slide.placeholders[1]
				subtitle.text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
			except Exception:
				pass

		sections: List[str] = deck.get("sections", [])
		bullets: List[List[str]] = deck.get("bullets", [])
		speaker_notes = deck.get("speaker_notes", [])
		generated_notes = deck.get("generated_notes", [])
		image_placeholders = deck.get("image_placeholders", [])
		media_refs = deck.get("media_refs", [])

		# Content slides
		for idx, section in enumerate(sections):
			# Try to reuse an existing template slide if available.
			target_index = idx + 1  # 0 is title slide
			if target_index < len(prs.slides):
				slide = prs.slides[target_index]
				title_shape = getattr(slide.shapes, "title", None)
				if title_shape is not None:
					title_shape.text = section
			else:
				content_layout = prs.slide_layouts[1]  # Title and Content
				slide = prs.slides.add_slide(content_layout)
				if slide.shapes.title:
					slide.shapes.title.text = section

			# Body text frame – fall back to a textbox if placeholder[1] is missing.
			try:
				text_frame = slide.placeholders[1].text_frame
			except Exception:
				box = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(8.0), Inches(4.5))
				text_frame = box.text_frame
			text_frame.clear()
			slide_bullets = bullets[idx] if idx < len(bullets) else []
			for i, bullet in enumerate(slide_bullets):
				p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
				p.text = bullet
				p.font.size = Pt(18)
				p.level = 0

			# Image placeholder captions (fallback text when no media available)
			placeholders = image_placeholders[idx] if idx < len(image_placeholders) else []
			for placeholder in placeholders:
				caption = placeholder.get("caption") or placeholder.get("marker") or placeholder.get("id")
				if not caption:
					continue
				p = text_frame.add_paragraph()
				p.text = f"[Image placeholder] {caption}"
				p.font.size = Pt(12)
				p.font.italic = True
				p.level = 1
				p.font.color.rgb = RGBColor(120, 120, 120)

			# Render stock / generated images when available
			slide_media = media_refs[idx] if idx < len(media_refs) else []
			if slide_media:
				# Use the first media URL for now; can be extended later.
				url = slide_media[0] if isinstance(slide_media[0], str) else None
				if url:
					try:
						response = requests.get(url, timeout=15)
						response.raise_for_status()
						img_bytes = response.content
						# Basic right-side placement; template-specific tuning can be
						# added later if needed.
						left = Inches(6.0)
						top = Inches(2.0)
						width = Inches(3.0)
						tmp_path = Path("_ppt_tmp_image.png")
						tmp_path.write_bytes(img_bytes)
						try:
							slide.shapes.add_picture(str(tmp_path), left, top, width=width)
						finally:
							try:
								tmp_path.unlink()
							except OSError:
								# Non-fatal if temp cleanup fails.
								pass
					except Exception:
						# If image download or placement fails, continue without blocking export.
						pass

			# Speaker notes priority
			notes_text = ""
			if idx < len(speaker_notes):
				note_entry = speaker_notes[idx]
				main_points = note_entry.get("main_points") or []
				talking_points = note_entry.get("talking_points") or []
				if main_points or talking_points:
					chunks = []
					if main_points:
						chunks.append("Main points: " + "; ".join(main_points[:4]))
					if talking_points:
						chunks.append("Talking points: " + "; ".join(talking_points[:4]))
					notes_text = "\n".join(chunks)
			if not notes_text and idx < len(generated_notes):
				notes_text = generated_notes[idx] or ""

			if notes_text:
				notes_frame = slide.notes_slide.notes_text_frame
				notes_frame.clear()
				notes_frame.text = notes_text.strip()

		return prs, f"deck_{str(object_id)}.pptx"
