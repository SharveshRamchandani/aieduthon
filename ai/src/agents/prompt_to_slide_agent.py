"""
Prompt-to-Slide Agent: Converts text prompts into structured slide decks
Uses LLM for intelligent content generation
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from ai_db import get_ai_db
from agents.text_generation_agent import TextGenerationAgent
from agents.media_integration_agent import MediaIntegrationAgent
from agents.template_selection_agent import TemplateSelectionAgent
from utils.fix_ppt_pipeline import prepare_slides_from_raw

logger = logging.getLogger(__name__)


@dataclass
class SlideContent:
    """Structure for individual slide content"""
    title: str
    bullets: List[str]
    examples: List[str]
    key_points: List[str]
    estimated_duration: int  # seconds
    images: List[Dict[str, Any]]
    notes: str = ""


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
    image_markers: List[Dict[str, Any]]
    template_path: Optional[str] = None
    template_metadata: Optional[Dict[str, Any]] = None


class PromptToSlideAgent:
    """Agent that converts teacher prompts into structured slide decks"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.prompts_collection = self.db["prompts"]
        self.slides_collection = self.db["slides"]
        self.text_agent = TextGenerationAgent()
        self.media_agent = MediaIntegrationAgent()
        self.template_agent = TemplateSelectionAgent()
        
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

            # Respect explicit slide count from context if provided
            user_requested_slides = None
            if context:
                user_requested_slides = context.get("estimated_slides")
                if isinstance(user_requested_slides, str):
                    try:
                        user_requested_slides = int(user_requested_slides)
                    except ValueError:
                        user_requested_slides = None
            if isinstance(user_requested_slides, (int, float)):
                user_requested_slides = int(user_requested_slides)
                if user_requested_slides > 0:
                    analysis["estimated_slides"] = max(3, min(30, user_requested_slides))
            
            # Generate structured content
            slide_deck, generation_result = self._generate_structured_content(analysis, prompt_text)

            # Select template and get selection metadata
            presentation_style = (context or {}).get("presentation_style", "educational")
            template_path = self.template_agent.select_template(
                subject=analysis.get("subject", ""),
                topics=analysis.get("key_topics", []),
                audience=analysis.get("target_audience"),
                presentation_style=presentation_style,
            )
            slide_deck.template_path = template_path
            
            # Store template selection metadata for adaptive use
            slide_deck.template_metadata = {
                "selected_template": template_path,
                "subject": analysis.get("subject", "general"),
                "style": presentation_style,
                "audience": analysis.get("target_audience", "general"),
                "topics": analysis.get("key_topics", [])
            }
            
            # Store generated slides with analysis for category tagging
            deck_id = self._store_slide_deck(prompt_id, slide_deck, user_id, context, analysis=analysis)
            
            # Generate media (images and diagrams) if requested
            generate_media = context.get("generate_media", True) if context else True
            if generate_media:
                try:
                    enriched_context = dict(context or {})
                    if generation_result.get("session_id"):
                        enriched_context["text_session_id"] = generation_result["session_id"]
                    if slide_deck.image_markers:
                        enriched_context["image_markers"] = slide_deck.image_markers
                    enriched_context.setdefault("auto_caption", True)
                    media_result = self.media_agent.generate_media_for_deck(
                        deck_id=deck_id,
                        context=enriched_context,
                        generate_images=True,
                        generate_diagrams=True
                    )
                    if media_result.get("success"):
                        logger.info(f"Generated media for deck {deck_id}")
                except Exception as e:
                    logger.warning(f"Media generation failed: {e}")
                    # Continue even if media generation fails
            
            # Emit analytics event
            self._emit_analytics_event(user_id, deck_id, "slides_generated", {
                "total_slides": slide_deck.total_slides,
                "estimated_duration": slide_deck.estimated_duration,
                "difficulty_level": slide_deck.difficulty_level,
                "template_path": template_path,
            })
            
            return {
                "success": True,
                "deck_id": deck_id,
                "prompt_id": prompt_id,
                "slide_deck": asdict(slide_deck),
                "metadata": {
                    "generated_at": datetime.utcnow(),
                    "locale": locale,
                    "total_slides": slide_deck.total_slides,
                    "text_session_id": generation_result.get("session_id"),
                    "raw_slide_json": generation_result.get("text"),
                    "template_path": template_path,
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
        Analyze prompt using LLM to extract key information
        """
        # Use LLM for intelligent analysis
        analysis_prompt = f"""Analyze this educational prompt and extract key information:

Prompt: {prompt_text}

Extract:
1. Subject/topic category (science, history, literature, geography, math, etc.)
2. Complexity level (beginner, intermediate, advanced)
3. Estimated number of slides needed (5-15)
4. Key topics to cover
5. Target audience level

Return JSON:
{{
  "subject": "subject category",
  "complexity": "beginner/intermediate/advanced",
  "estimated_slides": 5,
  "key_topics": ["topic1", "topic2"],
  "target_audience": "audience level"
}}"""
        
        # Allow a larger response so the model can return richer analysis
        # without being truncated at 512 tokens.
        result = self.text_agent.generate(analysis_prompt, context, max_length=2048)

        if result.get("success"):
            try:
                import re
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    if context:
                        analysis["target_audience"] = context.get("grade_level", analysis.get("target_audience", "general"))
                    analysis.setdefault("estimated_slides", max(5, len(analysis.get("key_topics", [])) or 8))
                    analysis.setdefault("key_topics", [])
                    return analysis
            except Exception as e:
                logger.warning(f"Failed to parse LLM analysis: {e}")
        
        # Fallback to heuristic analysis
        return self._heuristic_analyze_prompt(prompt_text, context)
    
    def _heuristic_analyze_prompt(self, prompt_text: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Fallback heuristic analysis"""
        words = prompt_text.lower().split()
        
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
    
    def _generate_structured_content(self, analysis: Dict[str, Any], original_prompt: str) -> Tuple[SlideDeck, Dict[str, Any]]:
        """Generate structured slide content using LLM.

        The original teacher prompt is passed through so that the LLM can
        stay tightly focused on the exact topic (e.g., \"photosynthesis\")
        instead of drifting to a broad subject category (e.g., \"science\").
        """
        
        subject = analysis.get("subject", "general")
        complexity = analysis.get("complexity", "intermediate")
        try:
            slide_count = int(analysis.get("estimated_slides") or 8)
        except (ValueError, TypeError):
            slide_count = 8
        slide_count = max(3, min(30, slide_count))
        topics = analysis.get("key_topics") or []
        audience = analysis["target_audience"]
        
        # Use LLM to generate slide content
        context = {
            "subject": subject,
            "grade_level": audience,
            "difficulty": complexity,
            "locale": "en"
        }
        
        # CRITICAL: Use the ACTUAL USER PROMPT as the primary input, NOT the subject
        # Subject is ONLY for context/metadata, NOT for content generation
        # The LLM should generate slides based on what the user actually asked for
        user_prompt = original_prompt.strip()
        
        # Build context that includes subject for metadata but uses actual prompt for content
        enhanced_context = context.copy()
        enhanced_context["subject_category"] = subject  # Only for context
        enhanced_context["user_prompt"] = user_prompt  # The actual content to generate
        
        result = self.text_agent.generate_slides_content(
            topic=user_prompt,  # Use ACTUAL prompt, not subject
            num_slides=slide_count,
            context=enhanced_context
        )

        # Second pass: Expand through Gemini first to make content richer
        if result.get("success") and result.get("text"):
            gemini_expanded = self.text_agent.expand_slide_content_gemini(
                result.get("text", ""),
                context=context,
                max_length=8192
            )
            if gemini_expanded.get("success") and gemini_expanded.get("text"):
                result = gemini_expanded
        
        # Third pass: Expand further through Deepseek for final elaboration
        if result.get("success") and result.get("text"):
            deepseek_expanded = self.text_agent.expand_slide_content(
                result.get("text", ""),
                context=context,
                max_length=8192
            )
            if deepseek_expanded.get("success") and deepseek_expanded.get("text"):
                result = deepseek_expanded
        
        # CRITICAL: Use the expanded content from LLM, not fallback templates
        if not result.get("success") or not result.get("text"):
            logger.error(f"LLM generation failed: {result.get('error', 'Unknown error')}")
            raise Exception(f"Failed to generate slide content: {result.get('error', 'LLM generation failed')}")
        
        # Parse the expanded LLM content
        try:
            prepared_payload = prepare_slides_from_raw(
                result["text"],
                desired_slide_count=slide_count
            )
            title = prepared_payload.get("meta", {}).get("presentation_title", f"{subject.title()} Presentation")
            slides_data = prepared_payload.get("slides", [])
            
            if not slides_data or len(slides_data) == 0:
                logger.error("LLM returned empty slides data")
                raise Exception("LLM generated empty slides - check LLM response")
            
        except Exception as exc:
            logger.error(f"Failed to parse LLM-generated slides: {exc}")
            logger.error(f"LLM response text: {result.get('text', '')[:500]}")
            raise Exception(f"Failed to parse expanded slide content: {exc}")
        
        # Build slides from LLM-generated content
        slides = []
        sections = []
        for slide_data in slides_data:
            section_title = slide_data.get("title", "")
            if not section_title:
                continue  # Skip slides without titles
            sections.append(section_title)
            
            # Get bullets from LLM-generated content
            bullets = slide_data.get("bullets", [])
            if not bullets:
                logger.warning(f"Slide '{section_title}' has no bullets, skipping")
                continue
            
            # Get the expanded content - combine bullets into full text content
            # This is the content after 3 passes (Gemini -> Gemini -> Deepseek)
            expanded_content = " ".join(bullets) if bullets else ""
            if slide_data.get("notes"):
                expanded_content += " " + slide_data.get("notes", "")
            
            slides.append(SlideContent(
                title=section_title,
                bullets=bullets,  # Keep for backward compatibility
                examples=slide_data.get("examples", []),
                key_points=slide_data.get("key_points", []),
                estimated_duration=self._estimate_slide_duration(complexity),
                images=slide_data.get("images", []),
                notes=expanded_content  # Store expanded content in notes field
            ))
        
        # If we still don't have enough slides, log error but don't use generic fallback
        if len(slides) < slide_count:
            logger.warning(f"LLM generated only {len(slides)} slides, requested {slide_count}")
            # Don't add generic fallback - use what LLM generated
        
        total_duration = sum(slide.estimated_duration for slide in slides)
        image_markers = result.get("image_markers", []) if isinstance(result, dict) else []
        
        raw_result: Dict[str, Any] = result if isinstance(result, dict) else {}
        
        return SlideDeck(
            title=title,
            sections=sections,
            slides=slides,
            total_slides=len(slides),
            estimated_duration=total_duration,
            difficulty_level=complexity,
            target_audience=audience,
            image_markers=image_markers
        ), raw_result
    
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
    
    def _get_subject_tags(self, subject: str) -> List[str]:
        """Get subject category tags for adaptive template use"""
        subject_map = {
            "science": ["science", "stem", "biology", "chemistry", "physics"],
            "biology": ["science", "biology", "life-sciences", "nature"],
            "chemistry": ["science", "chemistry", "lab", "experiments"],
            "physics": ["science", "physics", "mechanics", "energy"],
            "math": ["science", "mathematics", "numbers", "calculations"],
            "mathematics": ["science", "mathematics", "numbers", "calculations"],
            "history": ["history", "social-studies", "past", "events"],
            "literature": ["literature", "language-arts", "reading", "books"],
            "geography": ["geography", "social-studies", "places", "maps"],
            "business": ["business", "economics", "commerce", "finance"],
            "technology": ["technology", "tech", "computers", "digital"],
        }
        base_tags = subject_map.get(subject.lower(), [subject.lower()])
        return list(set(base_tags))
    
    def _get_style_tags(self, style: str) -> List[str]:
        """Get presentation style tags for adaptive template use"""
        style_map = {
            "academic": ["academic", "educational", "formal", "scholarly"],
            "educational": ["educational", "academic", "teaching", "learning"],
            "storytelling": ["storytelling", "narrative", "creative", "engaging"],
            "business_pitch": ["business", "pitch", "professional", "corporate"],
            "technical_briefing": ["technical", "detailed", "professional", "engineering"],
            "general": ["general", "informative", "standard"],
        }
        base_tags = style_map.get(style.lower(), [style.lower()])
        return list(set(base_tags))
    
    def _get_audience_tags(self, audience: str) -> List[str]:
        """Get audience category tags for adaptive template use"""
        audience_lower = audience.lower()
        tags = []
        if "grade" in audience_lower or "school" in audience_lower:
            tags.extend(["school", "education", "students"])
        if "college" in audience_lower or "university" in audience_lower:
            tags.extend(["college", "higher-education", "adults"])
        if "professional" in audience_lower or "business" in audience_lower:
            tags.extend(["professional", "corporate", "adults"])
        if not tags:
            tags = [audience_lower]
        return list(set(tags))
    
    def _store_slide_deck(self, prompt_id: str, slide_deck: SlideDeck, user_id: str, context: Optional[Dict] = None, analysis: Optional[Dict] = None) -> str:
        """Store generated slide deck in database with category tags for adaptive template use"""
        # Get analysis from context if not provided
        if analysis is None:
            analysis = {}
        
        deck_doc = {
            "promptId": prompt_id,
            "title": slide_deck.title,
            "sections": slide_deck.sections,
            "bullets": [slide.bullets for slide in slide_deck.slides],
            "examples": [slide.examples for slide in slide_deck.slides],
            "key_points": [slide.key_points for slide in slide_deck.slides],
            "image_placeholders": [slide.images for slide in slide_deck.slides],
            "image_markers": slide_deck.image_markers,
			"template_path": slide_deck.template_path,
            "generated_notes": [slide.notes for slide in slide_deck.slides],
            "speaker_notes": [],  # Will be filled by SpeakerNotesAgent
            "style": slide_deck.template_metadata.get("style", "default") if slide_deck.template_metadata else "default",
            "media_refs": [],  # Will be filled by MediaIntegrationAgent
            "diagram_refs": [],  # Will be filled by MediaIntegrationAgent
            "quiz_refs": [],  # Will be filled by QuizGenerationAgent
            "localized_versions": [],
            # Category tags for adaptive template use
            "categories": {
                "subject": analysis.get("subject", "general"),
                "subject_tags": self._get_subject_tags(analysis.get("subject", "general")),
                "style": slide_deck.template_metadata.get("style", "educational") if slide_deck.template_metadata else "educational",
                "style_tags": self._get_style_tags(slide_deck.template_metadata.get("style", "educational") if slide_deck.template_metadata else "educational"),
                "audience": slide_deck.target_audience,
                "audience_tags": self._get_audience_tags(slide_deck.target_audience),
                "complexity": slide_deck.difficulty_level,
                "topics": analysis.get("key_topics", []),
            },
            "template_metadata": slide_deck.template_metadata or {},
            "metadata": {
                "total_slides": slide_deck.total_slides,
                "estimated_duration": slide_deck.estimated_duration,
                "difficulty_level": slide_deck.difficulty_level,
                "target_audience": slide_deck.target_audience,
                "generated_at": datetime.utcnow(),
                "user_id": user_id,
                "context": context or {}
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
