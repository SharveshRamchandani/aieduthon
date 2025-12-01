from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from agents.speaker_notes_agent import SpeakerNotesAgent


class GenerateNotesRequest(BaseModel):
	userId: str
	audience_level: Optional[str] = None
	presentation_style: str = "educational"


router = APIRouter()


@router.post("/{deck_id}/speaker-notes")
def generate_speaker_notes(deck_id: str, body: GenerateNotesRequest):
	agent = SpeakerNotesAgent()
	result = agent.generate_speaker_notes(
		deck_id=deck_id,
		user_id=body.userId,
		audience_level=body.audience_level,
		presentation_style=body.presentation_style,
	)
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("error", "Speaker notes generation failed"))
	return {"ok": True, "totalSlides": result["metadata"]["total_slides"]}


