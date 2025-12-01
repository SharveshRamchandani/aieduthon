from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from agents.prompt_to_slide_agent import PromptToSlideAgent
from ai_db import get_ai_db
from bson.objectid import ObjectId


class CreateSlidesRequest(BaseModel):
	prompt: str = Field(min_length=3)
	userId: str
	locale: str = "en"
	context: Optional[Dict[str, Any]] = None


router = APIRouter()


@router.post("", status_code=201)
def create_slides(body: CreateSlidesRequest):
	agent = PromptToSlideAgent()
	result = agent.generate_slides(
		prompt_text=body.prompt,
		user_id=body.userId,
		locale=body.locale,
		context=body.context or {},
	)
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("error", "Slide generation failed"))
	return {"deckId": result["deck_id"], "promptId": result["prompt_id"]}


@router.get("/{deck_id}")
def get_deck(deck_id: str):
	db = get_ai_db()
	try:
		obj_id = ObjectId(deck_id)
	except Exception:
		raise HTTPException(status_code=400, detail="Invalid deck id")
	deck = db["slides"].find_one({"_id": obj_id})
	if not deck:
		raise HTTPException(status_code=404, detail="Deck not found")
	deck["_id"] = str(deck["_id"])  # simple serialization
	return deck


