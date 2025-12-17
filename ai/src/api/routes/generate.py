"""
New multimodal generation endpoints
"""

import json
from io import BytesIO
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from agents.text_generation_agent import TextGenerationAgent
from agents.image_generation_agent import ImageGenerationAgent
from agents.diagram_generation_agent import DiagramGenerationAgent
from agents.media_integration_agent import MediaIntegrationAgent

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

router = APIRouter()


class GenerateTextRequest(BaseModel):
	prompt: str = Field(min_length=1)
	context: Optional[Dict[str, Any]] = None
	max_length: Optional[int] = None
	temperature: Optional[float] = None
	use_cache: bool = True


class GenerateImageRequest(BaseModel):
	prompt: str = Field(min_length=1)
	width: Optional[int] = None
	height: Optional[int] = None
	negative_prompt: Optional[str] = None
	num_images: int = 1
	use_cache: bool = True


class GenerateDiagramRequest(BaseModel):
	diagram_type: str = Field(default="flowchart")
	description: str = Field(min_length=1)
	data: Optional[Dict[str, Any]] = None
	format: str = "png"
	style: Optional[str] = None


class GenerateSlidesRequest(BaseModel):
	prompt: str = Field(min_length=1)
	userId: str
	locale: str = "en"
	context: Optional[Dict[str, Any]] = None
	generate_images: bool = True
	generate_diagrams: bool = True


class GenerateNotesRequest(BaseModel):
	prompt: str = Field(min_length=1)
	userId: str
	audienceLevel: Optional[str] = None
	presentationStyle: str = "educational"
	context: Optional[Dict[str, Any]] = None
	max_length: Optional[int] = None
	temperature: Optional[float] = None


@router.post("/generate-text")
def generate_text(body: GenerateTextRequest):
	"""Generate text using LLM"""
	try:
		agent = TextGenerationAgent()
		result = agent.generate(
			prompt=body.prompt,
			context=body.context,
			max_length=body.max_length,
			temperature=body.temperature,
			use_cache=body.use_cache
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Text generation failed"))
		
		return {
			"success": True,
			"text": result.get("text"),
			"cached": result.get("cached", False),
			"model": result.get("model")
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


def _create_notes_pdf(notes_data: Dict[str, Any], output_path: Path) -> Path:
	"""Create a PDF from notes data using reportlab."""
	if not HAS_REPORTLAB:
		raise HTTPException(
			status_code=500,
			detail="reportlab library not installed. Install with: pip install reportlab"
		)
	
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
	styles = getSampleStyleSheet()
	
	# Custom styles
	title_style = ParagraphStyle(
		'CustomTitle',
		parent=styles['Heading1'],
		fontSize=24,
		textColor='#1a1a1a',
		spaceAfter=30,
		alignment=TA_CENTER
	)
	
	heading_style = ParagraphStyle(
		'CustomHeading',
		parent=styles['Heading2'],
		fontSize=16,
		textColor='#2c3e50',
		spaceAfter=12,
		spaceBefore=20
	)
	
	body_style = ParagraphStyle(
		'CustomBody',
		parent=styles['Normal'],
		fontSize=11,
		leading=14,
		spaceAfter=10
	)
	
	bullet_style = ParagraphStyle(
		'CustomBullet',
		parent=styles['Normal'],
		fontSize=11,
		leftIndent=20,
		bulletIndent=10,
		leading=14,
		spaceAfter=6
	)
	
	story = []
	
	# Title
	title = notes_data.get("title", "Lesson Notes")
	story.append(Paragraph(title, title_style))
	story.append(Spacer(1, 0.3*inch))
	
	# Overview
	overview = notes_data.get("overview", "")
	if overview:
		story.append(Paragraph("<b>Overview</b>", heading_style))
		story.append(Paragraph(overview.replace('\n', '<br/>'), body_style))
		story.append(Spacer(1, 0.2*inch))
	
	# Sections
	sections = notes_data.get("sections", [])
	for section in sections:
		heading = section.get("heading", "")
		if heading:
			story.append(Paragraph(f"<b>{heading}</b>", heading_style))
		
		bullets = section.get("bullets", [])
		for bullet in bullets:
			story.append(Paragraph(f"• {bullet}", bullet_style))
		
		activity = section.get("activity", "")
		if activity:
			story.append(Spacer(1, 0.1*inch))
			story.append(Paragraph(f"<i>Activity:</i> {activity}", body_style))
		
		story.append(Spacer(1, 0.15*inch))
	
	# Key Takeaways
	key_takeaways = notes_data.get("key_takeaways", [])
	if key_takeaways:
		story.append(PageBreak())
		story.append(Paragraph("<b>Key Takeaways</b>", heading_style))
		for takeaway in key_takeaways:
			story.append(Paragraph(f"• {takeaway}", bullet_style))
		story.append(Spacer(1, 0.2*inch))
	
	# Reflection Questions
	reflection_questions = notes_data.get("reflection_questions", [])
	if reflection_questions:
		story.append(Paragraph("<b>Reflection Questions</b>", heading_style))
		for i, question in enumerate(reflection_questions, 1):
			story.append(Paragraph(f"{i}. {question}", body_style))
	
	# Build PDF
	doc.build(story)
	
	# Write to file
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'wb') as f:
		f.write(buffer.getvalue())
	
	return output_path


@router.post("/generate-notes")
def generate_notes(body: GenerateNotesRequest):
	"""Generate detailed lesson notes directly from the original prompt and return as downloadable PDF."""
	try:
		agent = TextGenerationAgent()

		notes_prompt = f"""You are an expert instructional designer. Based on the following presentation prompt, write detailed lesson notes that a teacher can read verbatim. Include:
1. A concise session overview
2. 4-6 sections with headings, bullet points, and key facts
3. Hands-on examples or classroom activities
4. Key takeaways and reflection questions

Audience level: {body.audienceLevel or 'intermediate'}
Presentation style: {body.presentationStyle}

Prompt: {body.prompt}

Return valid JSON with this schema:
{{
  "title": "string",
  "overview": "string",
  "sections": [
    {{
      "heading": "string",
      "bullets": ["...", "..."],
      "activity": "string"
    }}
  ],
  "key_takeaways": ["...", "..."],
  "reflection_questions": ["...", "..."]
}}"""

		result = agent.generate(
			prompt=notes_prompt,
			context=body.context,
			max_length=body.max_length or 4096,
			temperature=body.temperature or 0.8,
			use_cache=False,
		)

		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Notes generation failed"))

		parsed_notes = _extract_json_payload(result.get("text", ""))
		
		# Generate PDF
		output_dir = Path("out/notes")
		output_dir.mkdir(parents=True, exist_ok=True)
		timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
		title_safe = parsed_notes.get("title", "notes").replace(" ", "_")[:50]
		pdf_filename = f"notes_{title_safe}_{timestamp}.pdf"
		pdf_path = output_dir / pdf_filename
		
		_create_notes_pdf(parsed_notes, pdf_path)
		
		# Return PDF as downloadable file
		return FileResponse(
			path=str(pdf_path),
			media_type="application/pdf",
			filename=pdf_filename,
			headers={"Content-Disposition": f'attachment; filename="{pdf_filename}"'}
		)
		
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-image")
def generate_image(body: GenerateImageRequest):
	"""Generate image using Stable Diffusion"""
	try:
		agent = ImageGenerationAgent()
		result = agent.generate(
			prompt=body.prompt,
			width=body.width,
			height=body.height,
			negative_prompt=body.negative_prompt,
			num_images=body.num_images,
			use_cache=body.use_cache
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Image generation failed"))
		
		return {
			"success": True,
			"urls": result.get("urls", []),
			"cached": result.get("cached", False),
			"model": result.get("model"),
			"mediaIds": result.get("media_ids", []),
			"captions": result.get("captions", []),
			"prompt": result.get("prompt"),
			"generatedAt": result.get("generated_at")
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-diagram")
def generate_diagram(body: GenerateDiagramRequest):
	"""Generate diagram using visualization tools"""
	try:
		agent = DiagramGenerationAgent()
		result = agent.generate(
			diagram_type=body.diagram_type,
			description=body.description,
			data=body.data,
			format=body.format,
			style=body.style
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Diagram generation failed"))
		
		return {
			"success": True,
			"file_path": result.get("file_path"),
			"diagram_id": result.get("diagram_id"),
			"type": result.get("type")
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-slides")
def generate_slides(body: GenerateSlidesRequest):
	"""Generate complete slides with text, images, and diagrams"""
	try:
		from agents.prompt_to_slide_agent import PromptToSlideAgent
		
		# Update context
		context = body.context or {}
		context["generate_media"] = body.generate_images or body.generate_diagrams
		
		# Generate slides
		agent = PromptToSlideAgent()
		result = agent.generate_slides(
			prompt_text=body.prompt,
			user_id=body.userId,
			locale=body.locale,
			context=context
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Slide generation failed"))
		
		return {
			"success": True,
			"deckId": result.get("deck_id"),
			"promptId": result.get("prompt_id"),
			"metadata": result.get("metadata")
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-media/{deck_id}")
def generate_media_for_deck(deck_id: str, generate_images: bool = True, generate_diagrams: bool = True):
	"""Generate media (images and diagrams) for an existing deck"""
	try:
		agent = MediaIntegrationAgent()
		result = agent.generate_media_for_deck(
			deck_id=deck_id,
			generate_images=generate_images,
			generate_diagrams=generate_diagrams
		)
		
		if not result.get("success"):
			raise HTTPException(status_code=500, detail=result.get("error", "Media generation failed"))
		
		return {
			"success": True,
			"media_refs": result.get("media_refs", []),
			"diagram_refs": result.get("diagram_refs", []),
			"media_metadata": result.get("media_metadata", [])
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


def _extract_json_payload(text: str) -> Dict[str, Any]:
	"""Extract JSON object from the LLM response."""
	if not text:
		return {}
	text = text.strip()
	if text.startswith("{"):
		try:
			return json.loads(text)
		except json.JSONDecodeError:
			pass
	start = text.find("{")
	end = text.rfind("}")
	if start != -1 and end != -1 and end > start:
		try:
			return json.loads(text[start : end + 1])
		except json.JSONDecodeError:
			return {"content": text}
	return {"content": text}

