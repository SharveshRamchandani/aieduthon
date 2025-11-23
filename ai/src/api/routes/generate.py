"""
New multimodal generation endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from agents.text_generation_agent import TextGenerationAgent
from agents.image_generation_agent import ImageGenerationAgent
from agents.diagram_generation_agent import DiagramGenerationAgent
from agents.media_integration_agent import MediaIntegrationAgent

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

