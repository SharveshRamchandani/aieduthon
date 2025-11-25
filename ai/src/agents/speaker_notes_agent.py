"""
Speaker Notes Agent: Generates detailed speaker notes for presentations
Uses LLM for intelligent note generation
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ai_db import get_ai_db
from bson.objectid import ObjectId
from agents.text_generation_agent import TextGenerationAgent

logger = logging.getLogger(__name__)


@dataclass
class SpeakerNote:
	"""Structure for speaker notes"""
	slide_title: str
	main_points: List[str]
	talking_points: List[str]
	examples: List[str]
	transitions: List[str]
	timing_notes: str
	audience_engagement: List[str]


class SpeakerNotesAgent:
	"""Agent that generates speaker notes for slide presentations"""
	
	def __init__(self):
		self.db = get_ai_db()
		self.slides_collection = self.db["slides"]
		self.text_agent = TextGenerationAgent()
		
	def generate_speaker_notes(self, 
						   deck_id: str, 
						   user_id: str,
						   audience_level: Optional[str] = None,
						   presentation_style: str = "educational") -> Dict[str, Any]:
		"""
		Generate speaker notes for slide deck
		
		Args:
			deck_id: ID of the slide deck
			user_id: User identifier
			audience_level: "beginner", "intermediate", "advanced"
			presentation_style: "educational", "persuasive", "informative"
			
		Returns:
			Dict with generated speaker notes and metadata
		"""
		try:
			# Get slide deck
			deck = self._get_slide_deck(deck_id)
			if not deck:
				return {"success": False, "error": "Slide deck not found"}
			
			# Analyze deck content and context
			context = self._analyze_deck_context(deck, audience_level, presentation_style)
			
			# Generate speaker notes for each slide
			speaker_notes = []
			for i, (section, bullets) in enumerate(zip(deck.get("sections", []), deck.get("bullets", []))):
				note = self._generate_slide_notes(section, bullets, context, i)
				speaker_notes.append(note)
			
			# Store speaker notes
			self._store_speaker_notes(deck_id, speaker_notes, user_id)
			
			# Emit analytics event
			self._emit_analytics_event(user_id, deck_id, "speaker_notes_generated", {
				"total_slides": len(speaker_notes),
				"audience_level": context["audience_level"],
				"presentation_style": presentation_style
			})
			
			return {
				"success": True,
				"speaker_notes": speaker_notes,
				"metadata": {
					"generated_at": datetime.utcnow(),
					"deck_id": deck_id,
					"total_slides": len(speaker_notes),
					"audience_level": context["audience_level"]
				}
			}
			
		except Exception as e:
			return {
				"success": False,
				"error": str(e),
				"speaker_notes": []
			}
	
	def _get_slide_deck(self, deck_id: str) -> Optional[Dict]:
		"""Get slide deck from database"""
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			return None
		return self.slides_collection.find_one({"_id": object_id})
	
	def _analyze_deck_context(self, deck: Dict, audience_level: Optional[str], presentation_style: str) -> Dict[str, Any]:
		"""Analyze deck context for note generation"""
		metadata = deck.get("metadata", {})
		
		# Determine audience level
		if not audience_level:
			audience_level = metadata.get("target_audience", "intermediate")
			if audience_level in ["school", "elementary"]:
				audience_level = "beginner"
			elif audience_level in ["college", "graduate"]:
				audience_level = "advanced"
			else:
				audience_level = "intermediate"
		
		# Determine difficulty level
		difficulty_level = metadata.get("difficulty_level", "intermediate")
		
		# Estimate presentation duration
		estimated_duration = metadata.get("estimated_duration", 0)
		
		return {
			"audience_level": audience_level,
			"difficulty_level": difficulty_level,
			"presentation_style": presentation_style,
			"estimated_duration": estimated_duration,
			"total_slides": len(deck.get("sections", [])),
			"subject": self._extract_subject_from_title(deck.get("title", ""))
		}
	
	def _extract_subject_from_title(self, title: str) -> str:
		"""Extract subject from deck title"""
		title_lower = title.lower()
		
		subjects = {
			"science": ["science", "physics", "chemistry", "biology", "math"],
			"history": ["history", "historical", "ancient", "medieval"],
			"literature": ["literature", "poetry", "novel", "story"],
			"geography": ["geography", "countries", "continents", "climate"]
		}
		
		for subject, keywords in subjects.items():
			if any(keyword in title_lower for keyword in keywords):
				return subject
		
		return "general"
	
	def _generate_slide_notes(self, section: str, bullets: List[str], context: Dict, slide_index: int) -> SpeakerNote:
		"""Generate speaker notes for a single slide using LLM"""
		
		# Use LLM to generate comprehensive speaker notes
		result = self.text_agent.generate_speaker_notes(
			slide_title=section,
			slide_content=bullets,
			context=context
		)
		
		if result.get("success") and result.get("notes"):
			notes_data = result["notes"]
			return SpeakerNote(
				slide_title=section,
				main_points=notes_data.get("main_points", []),
				talking_points=notes_data.get("talking_points", []),
				examples=notes_data.get("examples", []),
				transitions=notes_data.get("transitions", []),
				timing_notes=self._generate_timing_notes(section, bullets, context),
				audience_engagement=notes_data.get("engagement", [])
			)
		
		# Fallback to template-based generation
		return SpeakerNote(
			slide_title=section,
			main_points=self._generate_main_points(section, bullets, context),
			talking_points=self._generate_talking_points(section, bullets, context),
			examples=self._generate_examples(section, context),
			transitions=self._generate_transitions(section, slide_index, context),
			timing_notes=self._generate_timing_notes(section, bullets, context),
			audience_engagement=self._generate_audience_engagement(section, context)
		)
	
	def _generate_main_points(self, section: str, bullets: List[str], context: Dict) -> List[str]:
		"""Generate main points for the slide"""
		audience_level = context["audience_level"]
		
		if audience_level == "beginner":
			return [
				f"Start with a simple explanation of {section}",
				f"Focus on the basic concept behind {section}",
				f"Use everyday examples to illustrate {section}"
			]
		elif audience_level == "advanced":
			return [
				f"Provide detailed analysis of {section}",
				f"Discuss advanced concepts related to {section}",
				f"Connect {section} to broader theoretical frameworks"
			]
		else:  # intermediate
			return [
				f"Explain the key aspects of {section}",
				f"Provide practical examples of {section}",
				f"Connect {section} to real-world applications"
			]
	
	def _generate_talking_points(self, section: str, bullets: List[str], context: Dict) -> List[str]:
		"""Generate detailed talking points"""
		talking_points = []
		
		for i, bullet in enumerate(bullets):
			talking_points.append(f"Point {i+1}: {bullet}")
			talking_points.append(f"Elaborate on: {bullet}")
			
			if context["audience_level"] == "beginner":
				talking_points.append(f"Explain in simple terms: {bullet}")
			elif context["audience_level"] == "advanced":
				talking_points.append(f"Provide deeper analysis: {bullet}")
		
		return talking_points[:6]  # Limit to 6 talking points
	
	def _generate_examples(self, section: str, context: Dict) -> List[str]:
		"""Generate examples for the slide"""
		subject = context["subject"]
		audience_level = context["audience_level"]
		
		examples = []
		
		if subject == "science":
			if audience_level == "beginner":
				examples.extend([
					f"Everyday example of {section}",
					f"Simple experiment related to {section}"
				])
			else:
				examples.extend([
					f"Scientific case study of {section}",
					f"Research example involving {section}"
				])
		elif subject == "history":
			examples.extend([
				f"Historical event related to {section}",
				f"Timeline example of {section}"
			])
		else:
			examples.extend([
				f"Real-world example of {section}",
				f"Practical application of {section}"
			])
		
		return examples
	
	def _generate_transitions(self, section: str, slide_index: int, context: Dict) -> List[str]:
		"""Generate transition phrases"""
		total_slides = context["total_slides"]
		
		transitions = []
		
		if slide_index == 0:
			transitions.append(f"Let's begin by exploring {section}")
		elif slide_index == total_slides - 1:
			transitions.append(f"Finally, let's conclude with {section}")
		else:
			transitions.extend([
				f"Now let's move on to {section}",
				f"Building on what we've discussed, {section} is important because...",
				f"The next key point is {section}"
			])
		
		return transitions
	
	def _generate_timing_notes(self, section: str, bullets: List[str], context: Dict) -> str:
		"""Generate timing notes for the slide"""
		bullet_count = len(bullets)
		audience_level = context["audience_level"]
		
		# Base timing calculation
		base_time = max(30, bullet_count * 15)  # 15 seconds per bullet, min 30 seconds
		
		if audience_level == "beginner":
			timing = base_time + 30  # Extra time for explanations
		elif audience_level == "advanced":
			timing = base_time + 20  # Extra time for detailed analysis
		else:
			timing = base_time
		
		return f"Spend approximately {timing} seconds on this slide. Focus on clarity and engagement."
	
	def _generate_audience_engagement(self, section: str, context: Dict) -> List[str]:
		"""Generate audience engagement strategies"""
		audience_level = context["audience_level"]
		
		engagement_strategies = []
		
		if audience_level == "beginner":
			engagement_strategies.extend([
				f"Ask: 'Who has experienced {section}?'",
				f"Encourage questions about {section}",
				f"Use interactive examples for {section}"
			])
		elif audience_level == "advanced":
			engagement_strategies.extend([
				f"Pose analytical questions about {section}",
				f"Encourage discussion on {section}",
				f"Connect {section} to current research"
			])
		else:  # intermediate
			engagement_strategies.extend([
				f"Ask for examples of {section}",
				f"Encourage participation in {section} discussion",
				f"Use case studies for {section}"
			])
		
		return engagement_strategies
	
	def _store_speaker_notes(self, deck_id: str, speaker_notes: List[SpeakerNote], user_id: str):
		"""Store speaker notes in slide deck"""
		notes_data = []
		
		for note in speaker_notes:
			notes_data.append({
				"slide_title": note.slide_title,
				"main_points": note.main_points,
				"talking_points": note.talking_points,
				"examples": note.examples,
				"transitions": note.transitions,
				"timing_notes": note.timing_notes,
				"audience_engagement": note.audience_engagement
			})
		
		try:
			object_id = ObjectId(deck_id)
		except Exception:
			return
		self.slides_collection.update_one(
			{"_id": object_id},
			{"$set": {"speaker_notes": notes_data}}
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
			"service": "speaker_notes_agent"
		}
		
		analytics_collection.insert_one(event_doc)
