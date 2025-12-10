from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Tuple
from io import BytesIO

from agents.quiz_generation_agent import QuizGenerationAgent
from ai_db import get_ai_db
from bson.objectid import ObjectId

try:
	from reportlab.lib.pagesizes import letter
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	from reportlab.lib import colors
	HAS_REPORTLAB = True
except ImportError:
	HAS_REPORTLAB = False


class GenerateQuizRequest(BaseModel):
	userId: str
	quiz_type: str = "comprehensive"
	difficulty: Optional[str] = None


router = APIRouter()


@router.post("/{deck_id}/quizzes")
def generate_quizzes(deck_id: str, body: GenerateQuizRequest, download: Optional[str] = None):
	agent = QuizGenerationAgent()
	result = agent.generate_quiz(
		deck_id=deck_id,
		user_id=body.userId,
		quiz_type=body.quiz_type,
		difficulty=body.difficulty,
	)
	if not result.get("success"):
		raise HTTPException(status_code=500, detail=result.get("error", "Quiz generation failed"))
	
	# If download=pdf is requested, build and return a PDF
	if download and download.lower() == "pdf":
		if not HAS_REPORTLAB:
			raise HTTPException(status_code=500, detail="reportlab is required for quiz PDF export. Install with: pip install reportlab")
		
		db = get_ai_db()
		slides_coll = db["slides"]
		quizzes_coll = db["quizzes"]
		
		# Deck title for filename
		deck = slides_coll.find_one({"_id": ObjectId(deck_id)})
		deck_title = deck.get("title", "Quiz") if deck else "Quiz"
		
		# Fetch quiz docs
		quiz_docs: List[dict] = []
		for qid in result.get("quiz_ids", []):
			try:
				doc = quizzes_coll.find_one({"_id": ObjectId(qid)})
				if doc:
					quiz_docs.append(doc)
			except Exception:
				continue
		
		pdf_bytes, filename = _build_quiz_pdf(quiz_docs, deck_title)
		return Response(
			content=pdf_bytes,
			media_type="application/pdf",
			headers={
				"Content-Disposition": f'attachment; filename="{filename}"',
				"Content-Length": str(len(pdf_bytes))
			}
		)
	
	# Default JSON response
	return {
		"success": True,
		"quiz_ids": result.get("quiz_ids", []),
		"quizType": result.get("metadata", {}).get("quiz_type", "comprehensive")
	}


def _build_quiz_pdf(quiz_docs: List[dict], deck_title: str) -> Tuple[bytes, str]:
	"""Build a simple quiz PDF from quiz documents."""
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
	styles = getSampleStyleSheet()
	title_style = styles["Title"]
	question_style = ParagraphStyle(
		"Question",
		parent=styles["Heading2"],
		fontSize=14,
		spaceAfter=6,
		textColor=colors.HexColor("#1a1a1a"),
	)
	option_style = ParagraphStyle(
		"Option",
		parent=styles["Normal"],
		leftIndent=12,
		spaceAfter=4,
	)
	answer_style = ParagraphStyle(
		"Answer",
		parent=styles["Normal"],
		textColor=colors.HexColor("#0a6c3c"),
		spaceAfter=10,
	)

	story: List = []
	story.append(Paragraph(f"{deck_title} - Quiz", title_style))
	story.append(Spacer(1, 12))

	q_num = 1
	for quiz in quiz_docs:
		for question in quiz.get("questions", []):
			q_text = question.get("question_text", f"Question {q_num}")
			story.append(Paragraph(f"{q_num}. {q_text}", question_style))
			options = question.get("options", [])
			for idx, opt in enumerate(options):
				label = chr(ord("A") + idx)
				story.append(Paragraph(f"{label}) {opt}", option_style))
			correct = question.get("correct_answer")
			if correct:
				story.append(Paragraph(f"Answer: {correct}", answer_style))
			story.append(Spacer(1, 8))
			q_num += 1

	doc.build(story)
	pdf_bytes = buffer.getvalue()
	buffer.close()

	# Sanitize filename
	import re
	safe_title = re.sub(r"[^\w\s-]", "", deck_title)[:50].strip().replace(" ", "_") or "Quiz"
	filename = f"{safe_title}_quiz.pdf"
	return pdf_bytes, filename


