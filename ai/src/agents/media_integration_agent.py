"""
Media Integration Agent: Orchestrates image and diagram generation for slides
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

from agents.image_generation_agent import ImageGenerationAgent
from agents.diagram_generation_agent import DiagramGenerationAgent
from agents.text_generation_agent import TextGenerationAgent
from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class MediaIntegrationAgent:
    """Agent that orchestrates media generation and integration for slides"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.slides_collection = self.db["slides"]
        self.media_collection = self.db["media"]
        self.image_agent = ImageGenerationAgent()
        self.diagram_agent = DiagramGenerationAgent()
        self.text_agent = TextGenerationAgent()
    
    def generate_media_for_deck(self,
                                deck_id: str,
                                context: Optional[Dict] = None,
                                generate_images: bool = True,
                                generate_diagrams: bool = True) -> Dict[str, Any]:
        """
        Generate media (images and diagrams) for all slides in a deck
        
        Args:
            deck_id: ID of the slide deck
            context: Additional context (grade_level, subject, etc.)
            generate_images: Whether to generate images
            generate_diagrams: Whether to generate diagrams
        
        Returns:
            Dict with generated media references
        """
        try:
            context = context or {}
            auto_caption = context.get("auto_caption", True)
            session_id = context.get("text_session_id") or context.get("session_id")
            
            # Get slide deck
            from bson.objectid import ObjectId
            deck = self.slides_collection.find_one({"_id": ObjectId(deck_id)})
            if not deck:
                return {"success": False, "error": "Slide deck not found"}
            
            sections = deck.get("sections", [])
            bullets = deck.get("bullets", [])
            image_placeholders = deck.get("image_placeholders", [])
            
            media_refs = []
            diagram_refs = []
            media_metadata: List[List[Dict[str, Any]]] = []
            markers_by_index: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
            for marker in context.get("image_markers", []):
                index = marker.get("slide_index")
                if index is None and marker.get("slide_title") in sections:
                    try:
                        index = sections.index(marker["slide_title"])
                    except ValueError:
                        index = None
                if index is not None:
                    try:
                        markers_by_index[int(index)].append(marker)
                    except (ValueError, TypeError):
                        continue
            
            # Generate media for each slide
            for i in range(len(sections)):
                section = sections[i]
                slide_bullets = bullets[i] if i < len(bullets) else []
                slide_media: List[str] = []
                slide_diagrams: List[str] = []
                slide_media_details: List[Dict[str, Any]] = []
                
                # Generate image if enabled
                if generate_images:
                    placeholders = image_placeholders[i] if i < len(image_placeholders) else []
                    marker_payloads: List[Dict[str, Any]] = []
                    if markers_by_index.get(i):
                        marker_payloads.extend(markers_by_index[i])
                    if not marker_payloads:
                        for placeholder in placeholders:
                            marker_payload = {
                                **placeholder,
                                "slide_index": i,
                                "slide_title": section
                            }
                            marker_payloads.append(marker_payload)
                    
                    image_result = None
                    if marker_payloads:
                        marker_generation = self.image_agent.generate_from_markers(
                            markers=marker_payloads,
                            session_id=session_id,
                            context=context,
                            caption=auto_caption
                        )
                        image_result = marker_generation
                        if marker_generation.get("success"):
                            for item in marker_generation.get("items", []):
                                url = item.get("url")
                                if url:
                                    slide_media.append(url)
                                    slide_media_details.append(item)
                        else:
                            logger.warning(f"Marker-driven image generation failed for slide {i}: {marker_generation.get('errors')}")
                    
                    if not slide_media and (image_result is None or not image_result.get("success")):
                        fallback_result = self.image_agent.generate_for_slide(
                            section,
                            slide_bullets,
                            context
                        )
                        if fallback_result.get("success") and fallback_result.get("urls"):
                            slide_media.extend(fallback_result["urls"])
                            slide_media_details.append({
                                "prompt": fallback_result.get("prompt"),
                                "url": fallback_result["urls"][0],
                                "media_id": (fallback_result.get("media_ids") or [None])[0],
                                "caption": (fallback_result.get("captions") or [None])[0],
                                "source": "fallback"
                            })
                
                # Generate diagram if enabled and appropriate
                if generate_diagrams and self._should_generate_diagram(section, slide_bullets):
                    diagram_type = self._detect_diagram_type(section, slide_bullets)
                    diagram_result = self.diagram_agent.generate_for_slide(
                        section,
                        slide_bullets,
                        diagram_type
                    )
                    if diagram_result.get("success") and diagram_result.get("file_path"):
                        slide_diagrams.append(diagram_result["file_path"])
                
                media_refs.append(slide_media)
                diagram_refs.append(slide_diagrams)
                media_metadata.append(slide_media_details)
            
            # Update deck with media references
            self.slides_collection.update_one(
                {"_id": ObjectId(deck_id)},
                {
                    "$set": {
                        "media_refs": media_refs,
                        "diagram_refs": diagram_refs,
                        "media_metadata": media_metadata,
                        "media_generated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "success": True,
                "media_refs": media_refs,
                "diagram_refs": diagram_refs,
                "deck_id": deck_id,
                "media_metadata": media_metadata
            }
            
        except Exception as e:
            logger.error(f"Media generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "media_refs": [],
                "diagram_refs": []
            }
    
    def generate_media_for_slide(self,
                                 slide_title: str,
                                 slide_content: List[str],
                                 context: Optional[Dict] = None,
                                 diagram_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate media for a single slide
        
        Args:
            slide_title: Title of the slide
            slide_content: Content/bullets of the slide
            context: Additional context
            diagram_type: Type of diagram to generate (optional)
        
        Returns:
            Dict with generated media
        """
        try:
            media = {
                "images": [],
                "diagrams": []
            }
            
            # Generate image
            image_result = self.image_agent.generate_for_slide(
                slide_title,
                slide_content,
                context
            )
            if image_result.get("success") and image_result.get("urls"):
                media["images"] = image_result["urls"]
            
            # Generate diagram if appropriate
            if self._should_generate_diagram(slide_title, slide_content):
                diagram_type = diagram_type or self._detect_diagram_type(slide_title, slide_content)
                diagram_result = self.diagram_agent.generate_for_slide(
                    slide_title,
                    slide_content,
                    diagram_type
                )
                if diagram_result.get("success") and diagram_result.get("file_path"):
                    media["diagrams"].append(diagram_result["file_path"])
            
            return {
                "success": True,
                "media": media
            }
            
        except Exception as e:
            logger.error(f"Single slide media generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "media": {"images": [], "diagrams": []}
            }
    
    def _should_generate_diagram(self, title: str, content: List[str]) -> bool:
        """Determine if a diagram should be generated for this slide"""
        # Keywords that suggest a diagram would be helpful
        diagram_keywords = [
            "process", "flow", "cycle", "steps", "stages", "system",
            "hierarchy", "structure", "relationship", "comparison",
            "timeline", "sequence", "chart", "graph", "diagram"
        ]
        
        text = (title + " " + " ".join(content)).lower()
        return any(keyword in text for keyword in diagram_keywords)
    
    def _detect_diagram_type(self, title: str, content: List[str]) -> str:
        """Detect the appropriate diagram type for a slide"""
        text = (title + " " + " ".join(content)).lower()
        
        if any(keyword in text for keyword in ["cycle", "circular", "loop"]):
            return "cycle"
        elif any(keyword in text for keyword in ["hierarchy", "tree", "structure", "organization"]):
            return "hierarchy"
        elif any(keyword in text for keyword in ["chart", "graph", "data", "statistics"]):
            return "chart"
        elif any(keyword in text for keyword in ["process", "flow", "steps", "stages"]):
            return "flowchart"
        else:
            return "process"
    
    def suggest_media(self,
                     slide_title: str,
                     slide_content: List[str]) -> Dict[str, Any]:
        """Suggest what media should be generated for a slide"""
        suggestions = {
            "images": [],
            "diagrams": [],
            "diagram_type": None
        }
        
        # Suggest image
        image_prompt = self._generate_image_prompt(slide_title, slide_content)
        suggestions["images"] = [{
            "prompt": image_prompt,
            "reason": "Educational illustration to support slide content"
        }]
        
        # Suggest diagram if appropriate
        if self._should_generate_diagram(slide_title, slide_content):
            diagram_type = self._detect_diagram_type(slide_title, slide_content)
            suggestions["diagrams"] = [{
                "type": diagram_type,
                "reason": f"Visual representation would help explain {slide_title}"
            }]
            suggestions["diagram_type"] = diagram_type
        
        return suggestions
    
    def _generate_image_prompt(self, title: str, content: List[str]) -> str:
        """Generate image generation prompt from slide content"""
        # Use LLM to create a good image prompt
        content_summary = " ".join(content[:3])
        prompt = f"Create an image generation prompt for: {title}. {content_summary}"
        
        result = self.text_agent.generate(
            prompt,
            max_length=100,
            temperature=0.8
        )
        
        if result.get("success"):
            return result["text"].strip()
        else:
            # Fallback
            return f"Educational illustration: {title}"
    
    def link_media_to_slide(self,
                           deck_id: str,
                           slide_index: int,
                           media_urls: List[str],
                           diagram_paths: List[str]) -> Dict[str, Any]:
        """Link generated media to a specific slide"""
        try:
            from bson.objectid import ObjectId
            
            # Get current deck
            deck = self.slides_collection.find_one({"_id": ObjectId(deck_id)})
            if not deck:
                return {"success": False, "error": "Deck not found"}
            
            media_refs = deck.get("media_refs", [])
            diagram_refs = deck.get("diagram_refs", [])
            
            # Ensure lists are long enough
            while len(media_refs) <= slide_index:
                media_refs.append([])
            while len(diagram_refs) <= slide_index:
                diagram_refs.append([])
            
            # Update media references
            media_refs[slide_index] = media_urls
            diagram_refs[slide_index] = diagram_paths
            
            # Update deck
            self.slides_collection.update_one(
                {"_id": ObjectId(deck_id)},
                {
                    "$set": {
                        "media_refs": media_refs,
                        "diagram_refs": diagram_refs
                    }
                }
            )
            
            return {
                "success": True,
                "media_refs": media_refs,
                "diagram_refs": diagram_refs
            }
            
        except Exception as e:
            logger.error(f"Media linking failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

