from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from agents.quiz_generation_agent import QuizGenerationAgent


class GenerateQuizRequest(BaseModel):
	userId: str
	quiz_type: str = "comprehensive"
	difficulty: Optional[str] = None


router = APIRouter()


@router.post("/{deck_id}/quizzes")
def generate_quizzes(deck_id: str, body: GenerateQuizRequest):
	agent = QuizGenerationAgent()
	result = agent.generate_quiz(
		deck_id=deck_id,
		user_id=body.userId,
		quiz_type=body.quiz_type,
		difficulty=body.difficulty,
	)
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("error", "Quiz generation failed"))
	return {"quizIds": result["quiz_ids"], "quizType": result["metadata"]["quiz_type"]}


