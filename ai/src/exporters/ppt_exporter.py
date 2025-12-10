from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import base64

import requests
from bson.objectid import ObjectId
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class PPTExporter:
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]

	def export_deck(self, deck_id: str, output_dir: str = "..\\..\\out", user_name: str = "user") -> str:
		"""Export slide deck to disk (legacy behavior)."""
		prs, fname = self._build_presentation(deck_id, user_name)
		out_dir = Path(output_dir).resolve()
		out_dir.mkdir(parents=True, exist_ok=True)
		output_path = out_dir / fname
		prs.save(str(output_path))
		return str(output_path)

	def export_deck_to_bytes(self, deck_id: str, save_to_db: bool = True, user_name: str = "user", format_type: str = "pptx") -> Tuple[bytes, str]:
		"""Return PPTX or PDF content as bytes plus suggested filename. Optionally save to database.
		
		Args:
			deck_id: Deck ID
			save_to_db: Whether to save to database
			user_name: User name for filename
			format_type: "pptx" or "pdf"
		"""
		if format_type == "pdf":
			return self._export_to_pdf(deck_id, user_name)
		
		prs, fname = self._build_presentation(deck_id, user_name)
		buffer = BytesIO()
		prs.save(buffer)
		ppt_bytes = buffer.getvalue()
		
		# Save PPT to database if requested
		if save_to_db:
			self._save_ppt_to_db(deck_id, ppt_bytes, fname)
		
		return ppt_bytes, fname
	
	def _export_to_pdf(self, deck_id: str, user_name: str = "user") -> Tuple[bytes, str]:
		"""Convert PPTX to PDF preserving template and formatting.
		
		Uses LibreOffice headless mode to convert PPTX to PDF, which preserves
		all templates, formatting, colors, fonts, images, and layout exactly as in PPTX.
		Falls back to reportlab if LibreOffice is not available (but warns about loss of formatting).
		"""
		import re
		import tempfile
		import subprocess
		import shutil
		import platform
		
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			raise ValueError("Invalid deck_id. Must be a Mongo ObjectId hex string.")

		deck = self.slides_collection.find_one({"_id": object_id})
		if not deck:
			raise FileNotFoundError("Slide deck not found")
		
		title = deck.get("title", "AI Presentation")
		
		# Generate PPTX first (in memory)
		prs, pptx_filename = self._build_presentation(deck_id, user_name)
		
		# Generate filename: Topic_user_date.pdf
		safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip().replace(' ', '_')
		if not safe_title:
			safe_title = "Presentation"
		
		safe_user = re.sub(r'[^\w\s-]', '', user_name)[:30].strip().replace(' ', '_')
		if not safe_user:
			safe_user = "user"
		
		date_str = datetime.utcnow().strftime('%Y-%m-%d')
		filename = f"{safe_title}_{safe_user}_{date_str}.pdf"
		
		# Try LibreOffice conversion first (preserves template and formatting)
		try:
			return self._convert_pptx_to_pdf_libreoffice(prs, filename)
		except Exception as libreoffice_error:
			logger.warning(f"LibreOffice conversion failed: {libreoffice_error}. Falling back to reportlab (template/formatting may be lost).")
			# Fallback to reportlab (loses template but at least produces PDF)
			return self._convert_pptx_to_pdf_reportlab(prs, title, user_name, filename)
	
	def _convert_pptx_to_pdf_libreoffice(self, prs: Presentation, filename: str) -> Tuple[bytes, str]:
		"""Convert PPTX to PDF using LibreOffice headless mode - preserves all formatting."""
		import tempfile
		import subprocess
		import shutil
		import platform
		
		# Check if LibreOffice is available
		if platform.system() == "Windows":
			# Common LibreOffice paths on Windows
			libreoffice_paths = [
				r"C:\Program Files\LibreOffice\program\soffice.exe",
				r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
			]
			soffice = None
			for path in libreoffice_paths:
				if Path(path).exists():
					soffice = path
					break
			if not soffice:
				# Try to find in PATH
				soffice = shutil.which("soffice")
		else:
			# Linux/Mac - try to find in PATH
			soffice = shutil.which("soffice") or shutil.which("libreoffice")
		
		if not soffice:
			raise RuntimeError("LibreOffice not found. Install LibreOffice for PDF export with template preservation.")
		
		# Save PPTX to temporary file
		with tempfile.TemporaryDirectory() as temp_dir:
			pptx_path = Path(temp_dir) / "presentation.pptx"
			pdf_path = Path(temp_dir) / "presentation.pdf"
			
			# Save PPTX
			prs.save(str(pptx_path))
			
			# Convert using LibreOffice headless mode
			# --headless: Run without GUI
			# --convert-to pdf: Convert to PDF
			# --outdir: Output directory
			cmd = [
				soffice,
				"--headless",
				"--convert-to", "pdf",
				"--outdir", str(temp_dir),
				str(pptx_path)
			]
			
			try:
				result = subprocess.run(
					cmd,
					capture_output=True,
					text=True,
					timeout=60,  # 60 second timeout
					check=True
				)
			except subprocess.TimeoutExpired:
				raise RuntimeError("LibreOffice conversion timed out")
			except subprocess.CalledProcessError as e:
				raise RuntimeError(f"LibreOffice conversion failed: {e.stderr}")
			
			# Check if PDF was created
			if not pdf_path.exists():
				raise RuntimeError("LibreOffice did not produce PDF file")
			
			# Read PDF bytes
			with open(pdf_path, 'rb') as f:
				pdf_bytes = f.read()
			
			return pdf_bytes, filename
	
	def _convert_pptx_to_pdf_reportlab(self, prs: Presentation, title: str, user_name: str, filename: str) -> Tuple[bytes, str]:
		"""Fallback PDF conversion using reportlab - loses template but produces PDF."""
		try:
			from reportlab.lib.pagesizes import letter, A4
			from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
			from reportlab.lib.units import inch
			from reportlab.lib import colors
			from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
			from reportlab.lib.enums import TA_CENTER, TA_LEFT
		except ImportError:
			raise ImportError("reportlab is required for PDF export fallback. Install with: pip install reportlab")
		
		import tempfile
		
		# Create PDF buffer
		pdf_buffer = BytesIO()
		
		# Use letter size (8.5 x 11 inches) for slides
		doc = SimpleDocTemplate(
			pdf_buffer,
			pagesize=letter,
			rightMargin=0.5*inch,
			leftMargin=0.5*inch,
			topMargin=0.5*inch,
			bottomMargin=0.5*inch
		)
		
		styles = getSampleStyleSheet()
		
		# Custom styles for slides
		slide_title_style = ParagraphStyle(
			'SlideHeading',
			parent=styles['Heading2'],
			fontSize=24,
			textColor=colors.HexColor('#2c3e50'),
			spaceAfter=12,
			spaceBefore=10,
			fontName='Helvetica-Bold'
		)
		
		body_style = ParagraphStyle(
			'SlideBody',
			parent=styles['Normal'],
			fontSize=14,
			leading=18,
			spaceAfter=10,
			textColor=colors.HexColor('#333333'),
			fontName='Helvetica'
		)
		
		story = []
		temp_image_files = []  # Keep track of temp files to clean up after PDF is built
		
		# Process each slide
		for slide_idx, slide in enumerate(prs.slides):
			# Extract slide title
			slide_title = ""
			try:
				if slide.shapes.title:
					slide_title = slide.shapes.title.text.strip()
			except:
				pass
			
			# Add slide title if present
			if slide_title:
				story.append(Paragraph(slide_title, slide_title_style))
				story.append(Spacer(1, 0.2*inch))
			
			# Extract text content from all shapes
			text_content = []
			images = []
			
			for shape in slide.shapes:
				# Extract text from text boxes and placeholders
				if hasattr(shape, "text") and shape.text:
					text = shape.text.strip()
					if text and text != slide_title:  # Don't duplicate title
						text_content.append(text)
				
				# Extract images
				if hasattr(shape, "image"):
					try:
						image = shape.image
						image_bytes = image.blob
						# Save to temp file for reportlab
						with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
							tmp_img.write(image_bytes)
							img_path = tmp_img.name
							temp_image_files.append(img_path)  # Track for cleanup
							images.append((img_path, shape))
					except Exception as e:
						logger.debug(f"Failed to extract image from slide {slide_idx}: {e}")
			
			# Add text content
			for text in text_content:
				# Clean HTML-like tags and format
				clean_text = text.replace('\n', '<br/>')
				story.append(Paragraph(clean_text, body_style))
				story.append(Spacer(1, 0.1*inch))
			
			# Add images (if any)
			for img_path, shape in images:
				try:
					# Calculate image size (maintain aspect ratio, max width 7 inches)
					from PIL import Image as PILImage
					with PILImage.open(img_path) as pil_img:
						img_width_px, img_height_px = pil_img.size
						aspect = img_width_px / img_height_px
					
					# Get shape dimensions if available, otherwise use defaults
					try:
						shape_width = shape.width
						shape_height = shape.height
						# Convert EMU to inches (1 inch = 914400 EMU)
						shape_width_inch = shape_width / 914400
						shape_height_inch = shape_height / 914400
					except:
						shape_width_inch = 5.0
						shape_height_inch = 3.75
					
					# Use shape dimensions or calculate from image pixels
					max_width = 7 * inch
					max_height = 5 * inch
					
					# Use shape dimensions if reasonable, otherwise calculate from image
					if shape_width_inch > 0 and shape_height_inch > 0:
						width = min(shape_width_inch * inch, max_width)
						height = min(shape_height_inch * inch, max_height)
					else:
						# Calculate from image pixels (assuming 96 DPI)
						dpi = 96
						width_inch = img_width_px / dpi
						height_inch = img_height_px / dpi
						
						if width_inch > max_width / inch:
							width = max_width
							height = width / aspect
						elif height_inch > max_height / inch:
							height = max_height
							width = height * aspect
						else:
							width = width_inch * inch
							height = height_inch * inch
					
					story.append(RLImage(img_path, width=width, height=height))
					story.append(Spacer(1, 0.2*inch))
				except Exception as e:
					logger.debug(f"Failed to add image to PDF: {e}")
			
			# Add page break after each slide (except last)
			if slide_idx < len(prs.slides) - 1:
				story.append(PageBreak())
		
		# Build PDF (this is when ReportLab reads the image files)
		try:
			doc.build(story)
			pdf_bytes = pdf_buffer.getvalue()
		finally:
			# Clean up temp image files AFTER PDF is built
			for img_path in temp_image_files:
				try:
					if Path(img_path).exists():
						Path(img_path).unlink()
				except Exception as e:
					logger.debug(f"Failed to delete temp image file {img_path}: {e}")
		
		return pdf_bytes, filename
	
	def _save_ppt_to_db(self, deck_id: str, ppt_bytes: bytes, filename: str):
		"""Save generated PPT file to database"""
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			logger.warning(f"Invalid deck_id for PPT storage: {deck_id}")
			return
		
		# Update the deck document with PPT file info
		import base64
		ppt_base64 = base64.b64encode(ppt_bytes).decode("utf-8")
		
		update_data = {
			"ppt_file": ppt_base64,  # Store as base64 string
			"ppt_filename": filename,
			"ppt_generated_at": datetime.utcnow(),
			"ppt_size_bytes": len(ppt_bytes)
		}
		
		self.slides_collection.update_one(
			{"_id": object_id},
			{"$set": update_data}
		)
		logger.info(f"Saved PPT file to database for deck {deck_id}")

	def _build_presentation(self, deck_id: str, user_name: str = "user") -> Tuple[Presentation, str]:
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
		expanded_content: List[str] = deck.get("expanded_content", [])  # Content after 3 passes
		generated_notes = deck.get("generated_notes", [])  # This contains expanded content from 3 passes
		speaker_notes = deck.get("speaker_notes", [])
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
			
			# CRITICAL: Use expanded content (after 3 passes) instead of bullets
			# This is the actual expanded content from Gemini -> Gemini -> Deepseek
			# It's stored in generated_notes (which contains the expanded text after 3 passes)
			expanded_text = generated_notes[idx] if idx < len(generated_notes) else ""
			if not expanded_text and idx < len(expanded_content):
				expanded_text = expanded_content[idx]
			
			if expanded_text:
				# Place expanded content as paragraphs of text (not bullets)
				# Split into sentences for better formatting
				import re
				sentences = re.split(r'(?<=[.!?])\s+', expanded_text.strip())
				for i, sentence in enumerate(sentences):
					if sentence.strip():
						p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
						p.text = sentence.strip()
						p.font.size = Pt(16)
						p.level = 0
						p.space_after = Pt(6)
			else:
				# Fallback to bullets if expanded content not available
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

		# Generate filename: Topic_user_date.pptx
		title = deck.get("title", "Presentation")
		# Sanitize title for filename (remove special chars, limit length)
		import re
		safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip().replace(' ', '_')
		if not safe_title:
			safe_title = "Presentation"
		
		# Sanitize user name
		safe_user = re.sub(r'[^\w\s-]', '', user_name)[:30].strip().replace(' ', '_')
		if not safe_user:
			safe_user = "user"
		
		# Format date as YYYY-MM-DD
		date_str = datetime.utcnow().strftime('%Y-%m-%d')
		
		filename = f"{safe_title}_{safe_user}_{date_str}.pptx"
		
		return prs, filename
