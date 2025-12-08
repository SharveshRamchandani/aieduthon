from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from agents.speaker_notes_agent import SpeakerNotesAgent

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class GenerateNotesRequest(BaseModel):
	userId: str
	audience_level: Optional[str] = None
	presentation_style: str = "educational"


router = APIRouter()


def _create_speaker_notes_pdf(notes_data: List[Dict[str, Any]], deck_title: str, output_path: Path) -> Path:
	"""Create a PDF from speaker notes data."""
	if not HAS_REPORTLAB:
		raise HTTPException(
			status_code=500,
			detail="reportlab library not installed. Install with: pip install reportlab"
		)
	
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
	styles = getSampleStyleSheet()
	
	title_style = ParagraphStyle(
		'CustomTitle',
		parent=styles['Heading1'],
		fontSize=24,
		textColor='#1a1a1a',
		spaceAfter=30,
		alignment=TA_CENTER
	)
	
	slide_title_style = ParagraphStyle(
		'SlideTitle',
		parent=styles['Heading2'],
		fontSize=18,
		textColor='#2c3e50',
		spaceAfter=12,
		spaceBefore=25
	)
	
	heading_style = ParagraphStyle(
		'CustomHeading',
		parent=styles['Heading3'],
		fontSize=14,
		textColor='#34495e',
		spaceAfter=8,
		spaceBefore=15
	)
	
	body_style = ParagraphStyle(
		'CustomBody',
		parent=styles['Normal'],
		fontSize=11,
		leading=14,
		spaceAfter=8
	)
	
	bullet_style = ParagraphStyle(
		'CustomBullet',
		parent=styles['Normal'],
		fontSize=11,
		leftIndent=20,
		leading=14,
		spaceAfter=5
	)
	
	story = []
	
	# Title
	story.append(Paragraph(f"Speaker Notes: {deck_title}", title_style))
	story.append(Spacer(1, 0.3*inch))
	
	# Each slide's notes
	for idx, note in enumerate(notes_data, 1):
		# Handle both dict and SpeakerNote dataclass objects
		if isinstance(note, dict):
			slide_title = note.get("slide_title", f"Slide {idx}")
			main_points = note.get("main_points", [])
			talking_points = note.get("talking_points", [])
			examples = note.get("examples", [])
			transitions = note.get("transitions", [])
			timing = note.get("timing_notes", "")
			engagement = note.get("audience_engagement", [])
		else:
			# SpeakerNote dataclass object
			slide_title = getattr(note, "slide_title", f"Slide {idx}")
			main_points = getattr(note, "main_points", [])
			talking_points = getattr(note, "talking_points", [])
			examples = getattr(note, "examples", [])
			transitions = getattr(note, "transitions", [])
			timing = getattr(note, "timing_notes", "")
			engagement = getattr(note, "audience_engagement", [])
		
		story.append(Paragraph(f"<b>Slide {idx}: {slide_title}</b>", slide_title_style))
		
		# Main Points
		if main_points:
			story.append(Paragraph("<b>Main Points:</b>", heading_style))
			for point in main_points:
				story.append(Paragraph(f"• {point}", bullet_style))
			story.append(Spacer(1, 0.1*inch))
		
		# Talking Points
		if talking_points:
			story.append(Paragraph("<b>Talking Points:</b>", heading_style))
			for point in talking_points:
				story.append(Paragraph(f"• {point}", bullet_style))
			story.append(Spacer(1, 0.1*inch))
		
		# Examples
		if examples:
			story.append(Paragraph("<b>Examples:</b>", heading_style))
			for example in examples:
				story.append(Paragraph(f"• {example}", bullet_style))
			story.append(Spacer(1, 0.1*inch))
		
		# Transitions
		if transitions:
			story.append(Paragraph("<b>Transitions:</b>", heading_style))
			for transition in transitions:
				story.append(Paragraph(f"• {transition}", bullet_style))
			story.append(Spacer(1, 0.1*inch))
		
		# Timing Notes
		if timing:
			story.append(Paragraph(f"<b>Timing:</b> {timing}", body_style))
			story.append(Spacer(1, 0.1*inch))
		
		# Audience Engagement
		if engagement:
			story.append(Paragraph("<b>Audience Engagement:</b>", heading_style))
			for item in engagement:
				story.append(Paragraph(f"• {item}", bullet_style))
		
		# Page break between slides (except last)
		if idx < len(notes_data):
			story.append(PageBreak())
	
	# Build PDF
	doc.build(story)
	
	# Write to file
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'wb') as f:
		f.write(buffer.getvalue())
	
	return output_path


@router.post("/{deck_id}/speaker-notes")
def generate_speaker_notes(deck_id: str, body: GenerateNotesRequest):
	"""Generate speaker notes for a deck and return as downloadable PDF."""
	agent = SpeakerNotesAgent()
	result = agent.generate_speaker_notes(
		deck_id=deck_id,
		user_id=body.userId,
		audience_level=body.audience_level,
		presentation_style=body.presentation_style,
	)
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("error", "Speaker notes generation failed"))
	
	# Get deck title for PDF
	from ai_db import get_ai_db
	from bson.objectid import ObjectId
	db = get_ai_db()
	deck = db["slides"].find_one({"_id": ObjectId(deck_id)})
	deck_title = deck.get("title", "Presentation") if deck else "Presentation"
	
	# Generate PDF
	speaker_notes_raw = result.get("speaker_notes", [])
	# Convert SpeakerNote dataclass objects to dicts if needed
	speaker_notes = []
	for note in speaker_notes_raw:
		if isinstance(note, dict):
			speaker_notes.append(note)
		else:
			# Convert dataclass to dict
			from dataclasses import asdict
			speaker_notes.append(asdict(note))
	
	output_dir = Path("out/notes")
	output_dir.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
	title_safe = deck_title.replace(" ", "_")[:50]
	pdf_filename = f"speaker_notes_{title_safe}_{timestamp}.pdf"
	pdf_path = output_dir / pdf_filename
	
	_create_speaker_notes_pdf(speaker_notes, deck_title, pdf_path)
	
	# Return PDF as downloadable file - browser will automatically download it
	return FileResponse(
		path=str(pdf_path),
		media_type="application/pdf",
		filename=pdf_filename,
		headers={
			"Content-Disposition": f'attachment; filename="{pdf_filename}"',
			"Content-Type": "application/pdf"
		}
	)


@router.get("/{deck_id}/speaker-notes/download")
def download_speaker_notes(deck_id: str, file: str):
	"""Download the generated speaker notes PDF file."""
	output_dir = Path("out/notes")
	pdf_path = output_dir / file
	
	if not pdf_path.exists():
		raise HTTPException(status_code=404, detail="PDF file not found")
	
	return FileResponse(
		path=str(pdf_path),
		media_type="application/pdf",
		filename=file,
		headers={"Content-Disposition": f'attachment; filename="{file}"'}
	)


