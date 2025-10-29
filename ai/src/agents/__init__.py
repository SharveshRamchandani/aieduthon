"""
AI Agents for Educational Presentation Generation
"""

from .prompt_to_slide_agent import PromptToSlideAgent
from .quiz_generation_agent import QuizGenerationAgent
from .speaker_notes_agent import SpeakerNotesAgent

__all__ = [
	"PromptToSlideAgent",
	"QuizGenerationAgent", 
	"SpeakerNotesAgent",
]
