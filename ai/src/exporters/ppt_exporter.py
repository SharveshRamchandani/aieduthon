from datetime import datetime
from pathlib import Path
from typing import Dict, List

from bson.objectid import ObjectId
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from ai_db import get_ai_db


class PPTExporter:
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]

	def export_deck(self, deck_id: str, output_dir: str = "..\\..\\out") -> str:
		"""Export a slide deck from Mongo to a PPTX file.

		Returns the absolute path to the generated PPTX.
		"""
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			raise ValueError("Invalid deck_id. Must be a Mongo ObjectId hex string.")

		deck = self.slides_collection.find_one({"_id": object_id})
		if not deck:
			raise FileNotFoundError("Slide deck not found")

		prs = Presentation()

		# Title slide
		title_layout = prs.slide_layouts[0]
		slide = prs.slides.add_slide(title_layout)
		slide.shapes.title.text = deck.get("title", "AI Presentation")
		subtitle = slide.placeholders[1]
		subtitle.text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

		sections: List[str] = deck.get("sections", [])
		bullets: List[List[str]] = deck.get("bullets", [])
		speaker_notes = deck.get("speaker_notes", [])

		# Content slides
		for idx, section in enumerate(sections):
			content_layout = prs.slide_layouts[1]  # Title and Content
			slide = prs.slides.add_slide(content_layout)
			slide.shapes.title.text = section

			text_frame = slide.shapes.placeholders[1].text_frame
			text_frame.clear()
			for bullet in (bullets[idx] if idx < len(bullets) else []):
				p = text_frame.add_paragraph()
				p.text = bullet
				p.font.size = Pt(18)
				p.level = 0

			# Optional speaker notes into a small textbox
			if idx < len(speaker_notes) and speaker_notes[idx].get("main_points"):
				left = Inches(0.5)
				top = Inches(5.5)
				width = Inches(9)
				height = Inches(1)
				shape = slide.shapes.add_textbox(left, top, width, height)
				frame = shape.text_frame
				frame.word_wrap = True
				p = frame.paragraphs[0]
				p.text = "Notes: " + "; ".join(speaker_notes[idx]["main_points"][:3])
				p.font.size = Pt(12)
				p.font.color.rgb = RGBColor(80, 80, 80)

		# Save file
		out_dir = Path(output_dir).resolve()
		out_dir.mkdir(parents=True, exist_ok=True)
		fname = f"deck_{str(object_id)}.pptx"
		output_path = out_dir / fname
		prs.save(str(output_path))
		return str(output_path)
