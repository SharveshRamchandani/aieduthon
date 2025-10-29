"""
Quiz Generation Agent: Creates interactive quizzes from slide content
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ai_db import get_ai_db
from bson.objectid import ObjectId


@dataclass
class QuizQuestion:
	"""Structure for quiz questions"""
	question_text: str
	question_type: str  # "mcq", "fill_blank", "true_false"
	options: List[str]  # For MCQ
	correct_answer: str
	explanation: str
	difficulty: str
	topic: str


@dataclass
class Quiz:
	"""Complete quiz structure"""
	title: str
	questions: List[QuizQuestion]
	total_questions: int
	estimated_time: int  # minutes
	difficulty_level: str
	topics_covered: List[str]


class QuizGenerationAgent:
	"""Agent that generates quizzes from slide content"""
	
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]
		self.quizzes_collection = self.db["quizzes"]
		
	def generate_quiz(self, 
				 deck_id: str, 
				 user_id: str,
				 quiz_type: str = "comprehensive",
				 difficulty: Optional[str] = None) -> Dict[str, Any]:
		"""
		Generate quiz from slide deck
		
		Args:
			deck_id: ID of the slide deck
			user_id: User identifier
			quiz_type: "comprehensive", "per_topic", "final_only"
			difficulty: Override difficulty level
			
		Returns:
			Dict with generated quiz and metadata
		"""
		try:
			# Get slide deck
			deck = self._get_slide_deck(deck_id)
			if not deck:
				return {"success": False, "error": "Slide deck not found"}
			
			# Analyze slide content
			content_analysis = self._analyze_slide_content(deck)
			
			# Generate quiz based on type
			if quiz_type == "per_topic":
				quizzes = self._generate_per_topic_quizzes(deck, content_analysis, difficulty)
			elif quiz_type == "final_only":
				quizzes = [self._generate_final_quiz(deck, content_analysis, difficulty)]
			else:  # comprehensive
				quizzes = [self._generate_comprehensive_quiz(deck, content_analysis, difficulty)]
			
			# Store quizzes
			quiz_ids = []
			for quiz in quizzes:
				quiz_id = self._store_quiz(deck_id, quiz, user_id)
				quiz_ids.append(quiz_id)
			
			# Update slide deck with quiz references
			self._update_deck_quiz_refs(deck_id, quiz_ids)
			
			# Emit analytics event
			self._emit_analytics_event(user_id, deck_id, "quiz_generated", {
				"quiz_count": len(quizzes),
				"total_questions": sum(q.total_questions for q in quizzes),
				"quiz_type": quiz_type
			})
			
			return {
				"success": True,
				"quiz_ids": quiz_ids,
				"quizzes": quizzes,
				"metadata": {
					"generated_at": datetime.utcnow(),
					"deck_id": deck_id,
					"quiz_type": quiz_type
				}
			}
			
		except Exception as e:
			return {
				"success": False,
				"error": str(e),
				"quiz_ids": []
			}
	
	def _get_slide_deck(self, deck_id: str) -> Optional[Dict]:
		"""Get slide deck from database"""
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			return None
		return self.slides_collection.find_one({"_id": object_id})
	
	def _analyze_slide_content(self, deck: Dict) -> Dict[str, Any]:
		"""Analyze slide content to extract quiz-worthy concepts"""
		sections = deck.get("sections", [])
		bullets = deck.get("bullets", [])
		
		# Extract key concepts from bullets
		concepts = []
		for section_bullets in bullets:
			for bullet in section_bullets:
				# Simple concept extraction - in production, use NLP
				concepts.append({
					"text": bullet,
					"section": sections[len(concepts) % len(sections)] if sections else "General",
					"complexity": self._assess_concept_complexity(bullet)
				})
		
		return {
			"concepts": concepts,
			"sections": sections,
			"difficulty_level": deck.get("metadata", {}).get("difficulty_level", "intermediate"),
			"total_concepts": len(concepts)
		}
	
	def _assess_concept_complexity(self, text: str) -> str:
		"""Assess complexity of a concept"""
		# Simple heuristic - in production, use NLP analysis
		complex_indicators = ["analysis", "synthesis", "evaluation", "advanced", "complex"]
		simple_indicators = ["basic", "simple", "introduction", "overview"]
		
		text_lower = text.lower()
		
		if any(indicator in text_lower for indicator in complex_indicators):
			return "hard"
		elif any(indicator in text_lower for indicator in simple_indicators):
			return "easy"
		else:
			return "medium"
	
	def _generate_comprehensive_quiz(self, deck: Dict, analysis: Dict, difficulty: Optional[str]) -> Quiz:
		"""Generate comprehensive quiz covering all topics"""
		concepts = analysis["concepts"]
		deck_difficulty = difficulty or analysis["difficulty_level"]
		
		# Generate questions for key concepts
		questions = []
		for concept in concepts[:10]:  # Limit to 10 questions
			question = self._generate_question_for_concept(concept, deck_difficulty)
			if question:
				questions.append(question)
		
		return Quiz(
			title=f"{deck['title']} - Comprehensive Quiz",
			questions=questions,
			total_questions=len(questions),
			estimated_time=len(questions) * 2,  # 2 minutes per question
			difficulty_level=deck_difficulty,
			topics_covered=list(set(q.topic for q in questions))
		)
	
	def _generate_per_topic_quizzes(self, deck: Dict, analysis: Dict, difficulty: Optional[str]) -> List[Quiz]:
		"""Generate separate quiz for each topic/section"""
		sections = analysis["sections"]
		concepts = analysis["concepts"]
		deck_difficulty = difficulty or analysis["difficulty_level"]
		
		quizzes = []
		for section in sections:
			# Get concepts for this section
			section_concepts = [c for c in concepts if c["section"] == section]
			
			if section_concepts:
				questions = []
				for concept in section_concepts[:5]:  # Max 5 questions per section
					question = self._generate_question_for_concept(concept, deck_difficulty)
					if question:
						questions.append(question)
				
				if questions:
					quiz = Quiz(
						title=f"{section} - Quiz",
						questions=questions,
						total_questions=len(questions),
						estimated_time=len(questions) * 2,
						difficulty_level=deck_difficulty,
						topics_covered=[section]
					)
					quizzes.append(quiz)
		
		return quizzes
	
	def _generate_final_quiz(self, deck: Dict, analysis: Dict, difficulty: Optional[str]) -> Quiz:
		"""Generate final assessment quiz"""
		concepts = analysis["concepts"]
		deck_difficulty = difficulty or analysis["difficulty_level"]
		
		# Select most important concepts for final quiz
		important_concepts = concepts[:8]  # Top 8 concepts
		
		questions = []
		for concept in important_concepts:
			question = self._generate_question_for_concept(concept, deck_difficulty)
			if question:
				questions.append(question)
		
		return Quiz(
			title=f"{deck['title']} - Final Assessment",
			questions=questions,
			total_questions=len(questions),
			estimated_time=len(questions) * 3,  # 3 minutes per question for final
			difficulty_level=deck_difficulty,
			topics_covered=list(set(q.topic for q in questions))
		)
	
	def _generate_question_for_concept(self, concept: Dict, difficulty: str) -> Optional[QuizQuestion]:
		"""Generate a quiz question for a concept"""
		concept_text = concept["text"]
		section = concept["section"]
		concept_complexity = concept["complexity"]
		
		# Determine question type based on complexity
		if concept_complexity == "easy":
			question_type = "true_false"
		elif concept_complexity == "medium":
			question_type = "mcq"
		else:
			question_type = "fill_blank"
		
		# Generate question based on type
		if question_type == "mcq":
			return self._generate_mcq_question(concept_text, section, difficulty)
		elif question_type == "true_false":
			return self._generate_true_false_question(concept_text, section, difficulty)
		elif question_type == "fill_blank":
			return self._generate_fill_blank_question(concept_text, section, difficulty)
		
		return None
	
	def _generate_mcq_question(self, concept: str, topic: str, difficulty: str) -> QuizQuestion:
		"""Generate multiple choice question"""
		# In production, use LLM to generate contextual questions
		question_text = f"Which of the following best describes: {concept}?"
		
		options = [
			f"Option A related to {concept}",
			f"Option B related to {concept}",
			f"Option C related to {concept}",
			f"Option D related to {concept}"
		]
		
		correct_answer = options[0]  # In production, generate correct answer
		explanation = f"This is the correct answer because it accurately represents {concept}."
		
		return QuizQuestion(
			question_text=question_text,
			question_type="mcq",
			options=options,
			correct_answer=correct_answer,
			explanation=explanation,
			difficulty=difficulty,
			topic=topic
		)
	
	def _generate_true_false_question(self, concept: str, topic: str, difficulty: str) -> QuizQuestion:
		"""Generate true/false question"""
		question_text = f"True or False: {concept} is a valid concept."
		
		return QuizQuestion(
			question_text=question_text,
			question_type="true_false",
			options=["True", "False"],
			correct_answer="True",
			explanation=f"This statement is true because {concept} is indeed a valid concept.",
			difficulty=difficulty,
			topic=topic
		)
	
	def _generate_fill_blank_question(self, concept: str, topic: str, difficulty: str) -> QuizQuestion:
		"""Generate fill-in-the-blank question"""
		# Extract key term from concept
		words = concept.split()
		key_term = words[0] if words else "concept"
		
		question_text = f"Complete the following: {concept.replace(key_term, '_____')}"
		
		return QuizQuestion(
			question_text=question_text,
			question_type="fill_blank",
			options=[],
			correct_answer=key_term,
			explanation=f"The correct answer is '{key_term}' because it completes the concept accurately.",
			difficulty=difficulty,
			topic=topic
		)
	
	def _store_quiz(self, deck_id: str, quiz: Quiz, user_id: str) -> str:
		"""Store quiz in database"""
		quiz_doc = {
			"slideId": deck_id,
			"title": quiz.title,
			"questions": [
				{
					"question_text": q.question_text,
					"question_type": q.question_type,
					"options": q.options,
					"correct_answer": q.correct_answer,
					"explanation": q.explanation,
					"difficulty": q.difficulty,
					"topic": q.topic
				}
				for q in quiz.questions
			],
			"accuracy_stats": {
				"total_attempts": 0,
				"correct_attempts": 0,
				"average_score": 0.0
			},
			"live_quiz_export": None,  # Will be filled when exported to Google Forms
			"injected_position": "after_section",  # or "final"
			"metadata": {
				"total_questions": quiz.total_questions,
				"estimated_time": quiz.estimated_time,
				"difficulty_level": quiz.difficulty_level,
				"topics_covered": quiz.topics_covered,
				"generated_at": datetime.utcnow(),
				"user_id": user_id
			}
		}
		
		result = self.quizzes_collection.insert_one(quiz_doc)
		return str(result.inserted_id)
	
	def _update_deck_quiz_refs(self, deck_id: str, quiz_ids: List[str]):
		"""Update slide deck with quiz references"""
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			return
		self.slides_collection.update_one(
			{"_id": object_id},
			{"$set": {"quiz_refs": quiz_ids}}
		)
	
	def _emit_analytics_event(self, user_id: str, deck_id: str, event_type: str, data: Dict):
		"""Emit analytics event"""
		analytics_collection = self.db["analytics"]
		
		event_doc = {
			"userId": user_id,
			"timestamp": datetime.utcnow(),
			"deckId": deck_id,
			"event_type": event_type,
			"data": data,
			"service": "quiz_generation_agent"
		}
		
		analytics_collection.insert_one(event_doc)
