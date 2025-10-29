"""
Prompt-to-Slide Agent: Converts text prompts into structured slide decks
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ai_db import get_ai_db


@dataclass
class SlideContent:
    """Structure for individual slide content"""
    title: str
    bullets: List[str]
    examples: List[str]
    key_points: List[str]
    estimated_duration: int  # seconds


@dataclass
class SlideDeck:
    """Complete slide deck structure"""
    title: str
    sections: List[str]
    slides: List[SlideContent]
    total_slides: int
    estimated_duration: int
    difficulty_level: str
    target_audience: str


class PromptToSlideAgent:
    """Agent that converts teacher prompts into structured slide decks"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.prompts_collection = self.db["prompts"]
        self.slides_collection = self.db["slides"]
        
    def generate_slides(self, 
                       prompt_text: str, 
                       user_id: str,
                       locale: str = "en",
                       context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main method to generate slides from prompt
        
        Args:
            prompt_text: Teacher's input text
            user_id: User identifier
            locale: Language/locale (en, hi, ta, etc.)
            context: Additional context (grade, subject, etc.)
            
        Returns:
            Dict with generated slide deck and metadata
        """
        try:
            # Store original prompt
            prompt_id = self._store_prompt(prompt_text, user_id, locale, context)
            
            # Analyze prompt and extract requirements
            analysis = self._analyze_prompt(prompt_text, context)
            
            # Generate structured content
            slide_deck = self._generate_structured_content(analysis)
            
            # Store generated slides
            deck_id = self._store_slide_deck(prompt_id, slide_deck, user_id)
            
            # Emit analytics event
            self._emit_analytics_event(user_id, deck_id, "slides_generated", {
                "total_slides": slide_deck.total_slides,
                "estimated_duration": slide_deck.estimated_duration,
                "difficulty_level": slide_deck.difficulty_level
            })
            
            return {
                "success": True,
                "deck_id": deck_id,
                "prompt_id": prompt_id,
                "slide_deck": slide_deck,
                "metadata": {
                    "generated_at": datetime.utcnow(),
                    "locale": locale,
                    "total_slides": slide_deck.total_slides
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deck_id": None
            }
    
    def _store_prompt(self, prompt_text: str, user_id: str, locale: str, context: Optional[Dict]) -> str:
        """Store the original prompt in database"""
        prompt_doc = {
            "userId": user_id,
            "prompt_text": prompt_text,
            "timestamp": datetime.utcnow(),
            "locale": locale,
            "context": context or {},
            "status": "processed"
        }
        
        result = self.prompts_collection.insert_one(prompt_doc)
        return str(result.inserted_id)
    
    def _analyze_prompt(self, prompt_text: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Analyze prompt to extract key information
        In production, this would use NLP/LLM for analysis
        """
        # Basic analysis - in production, use spaCy + LLM
        words = prompt_text.lower().split()
        
        # Detect subject/topic
        subject_keywords = {
            "science": ["science", "physics", "chemistry", "biology", "math", "mathematics"],
            "history": ["history", "historical", "ancient", "medieval", "modern"],
            "literature": ["literature", "poetry", "novel", "story", "writing"],
            "geography": ["geography", "countries", "continents", "climate", "environment"]
        }
        
        detected_subject = "general"
        for subject, keywords in subject_keywords.items():
            if any(keyword in words for keyword in keywords):
                detected_subject = subject
                break
        
        # Detect complexity level
        complexity_indicators = {
            "beginner": ["basic", "introduction", "simple", "elementary"],
            "intermediate": ["advanced", "detailed", "comprehensive", "analysis"],
            "expert": ["expert", "research", "thesis", "doctoral", "graduate"]
        }
        
        complexity = "intermediate"
        for level, indicators in complexity_indicators.items():
            if any(indicator in words for indicator in indicators):
                complexity = level
                break
        
        # Estimate slide count based on prompt length and complexity
        base_slides = max(5, len(words) // 20)
        if complexity == "beginner":
            slide_count = min(base_slides, 10)
        elif complexity == "expert":
            slide_count = max(base_slides, 15)
        else:
            slide_count = base_slides
        
        return {
            "subject": detected_subject,
            "complexity": complexity,
            "estimated_slides": slide_count,
            "key_topics": self._extract_topics(prompt_text),
            "target_audience": context.get("grade_level", "general") if context else "general"
        }
    
    def _extract_topics(self, prompt_text: str) -> List[str]:
        """Extract main topics from prompt text"""
        # Simple topic extraction - in production, use spaCy NER
        sentences = prompt_text.split('.')
        topics = []
        
        for sentence in sentences[:3]:  # First 3 sentences
            words = sentence.strip().split()
            if len(words) > 3:
                # Take first few meaningful words as topic
                topic = ' '.join(words[:4]).strip()
                if topic:
                    topics.append(topic)
        
        return topics[:5]  # Max 5 topics
    
    def _generate_structured_content(self, analysis: Dict[str, Any]) -> SlideDeck:
        """Generate structured slide content based on analysis"""
        
        subject = analysis["subject"]
        complexity = analysis["complexity"]
        slide_count = analysis["estimated_slides"]
        topics = analysis["key_topics"]
        audience = analysis["target_audience"]
        
        # Generate title
        title = f"{subject.title()} Presentation"
        if topics:
            title = f"{topics[0]} - {subject.title()}"
        
        # Generate sections
        sections = self._generate_sections(subject, topics, slide_count)
        
        # Generate individual slides
        slides = []
        for i, section in enumerate(sections):
            slide_content = SlideContent(
                title=f"{i+1}. {section}",
                bullets=self._generate_bullets(section, subject, complexity),
                examples=self._generate_examples(section, subject, audience),
                key_points=self._generate_key_points(section, subject),
                estimated_duration=self._estimate_slide_duration(complexity)
            )
            slides.append(slide_content)
        
        # Calculate total duration
        total_duration = sum(slide.estimated_duration for slide in slides)
        
        return SlideDeck(
            title=title,
            sections=sections,
            slides=slides,
            total_slides=len(slides),
            estimated_duration=total_duration,
            difficulty_level=complexity,
            target_audience=audience
        )
    
    def _generate_sections(self, subject: str, topics: List[str], slide_count: int) -> List[str]:
        """Generate section titles"""
        if topics:
            return topics[:slide_count]
        
        # Default sections based on subject
        default_sections = {
            "science": ["Introduction", "Key Concepts", "Examples", "Applications", "Summary"],
            "history": ["Background", "Timeline", "Key Events", "Impact", "Conclusion"],
            "literature": ["Overview", "Analysis", "Themes", "Characters", "Significance"],
            "geography": ["Location", "Climate", "Resources", "Population", "Culture"]
        }
        
        sections = default_sections.get(subject, ["Introduction", "Main Points", "Examples", "Summary"])
        return sections[:slide_count]
    
    def _generate_bullets(self, section: str, subject: str, complexity: str) -> List[str]:
        """Generate bullet points for a section"""
        # In production, use LLM to generate contextual bullets
        base_bullets = [
            f"Key concept related to {section}",
            f"Important aspect of {section}",
            f"Practical application of {section}"
        ]
        
        if complexity == "beginner":
            return base_bullets[:2]
        elif complexity == "expert":
            return base_bullets + [f"Advanced consideration for {section}"]
        else:
            return base_bullets
    
    def _generate_examples(self, section: str, subject: str, audience: str) -> List[str]:
        """Generate examples for a section"""
        # In production, use LLM with audience context
        return [
            f"Real-world example of {section}",
            f"Case study related to {section}"
        ]
    
    def _generate_key_points(self, section: str, subject: str) -> List[str]:
        """Generate key points for a section"""
        return [
            f"Main takeaway from {section}",
            f"Critical understanding of {section}"
        ]
    
    def _estimate_slide_duration(self, complexity: str) -> int:
        """Estimate duration for a slide in seconds"""
        duration_map = {
            "beginner": 30,
            "intermediate": 45,
            "expert": 60
        }
        return duration_map.get(complexity, 45)
    
    def _store_slide_deck(self, prompt_id: str, slide_deck: SlideDeck, user_id: str) -> str:
        """Store generated slide deck in database"""
        deck_doc = {
            "promptId": prompt_id,
            "title": slide_deck.title,
            "sections": slide_deck.sections,
            "bullets": [slide.bullets for slide in slide_deck.slides],
            "speaker_notes": [],  # Will be filled by SpeakerNotesAgent
            "style": "default",  # Will be filled by TemplateSelectionAgent
            "media_refs": [],  # Will be filled by MediaIntegrationAgent
            "quiz_refs": [],  # Will be filled by QuizGenerationAgent
            "localized_versions": [],
            "metadata": {
                "total_slides": slide_deck.total_slides,
                "estimated_duration": slide_deck.estimated_duration,
                "difficulty_level": slide_deck.difficulty_level,
                "target_audience": slide_deck.target_audience,
                "generated_at": datetime.utcnow(),
                "user_id": user_id
            }
        }
        
        result = self.slides_collection.insert_one(deck_doc)
        return str(result.inserted_id)
    
    def _emit_analytics_event(self, user_id: str, deck_id: str, event_type: str, data: Dict):
        """Emit analytics event"""
        analytics_collection = self.db["analytics"]
        
        event_doc = {
            "userId": user_id,
            "timestamp": datetime.utcnow(),
            "deckId": deck_id,
            "event_type": event_type,
            "data": data,
            "service": "prompt_to_slide_agent"
        }
        
        analytics_collection.insert_one(event_doc)
