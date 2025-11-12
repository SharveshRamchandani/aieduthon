"""
Image Generation Agent: Uses Stable Diffusion for educational image generation
"""

import logging
import io
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from PIL import Image
import hashlib
import json

from bson import ObjectId

from agents.model_manager import get_model_manager
from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class ImageGenerationAgent:
    """Agent that generates educational images using Stable Diffusion"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.media_collection = self.db["media"]
        self.cache_collection = self.db["ai_cache"]
        self.outputs_collection = self.db["ai_outputs"]
        self.model_manager = get_model_manager()
        self.image_model = None
        self.vision_model = None
        self._ensure_models_loaded()
        self.output_dir = Path("out/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _ensure_models_loaded(self):
        """Ensure image models are loaded (lazy loading)"""
        # Don't load model on init - only when actually needed
        pass
    
    def _get_cache_key(self, prompt: str, width: int, height: int) -> str:
        """Generate cache key for image prompt"""
        cache_data = f"{prompt}_{width}_{height}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if image exists in cache"""
        try:
            cached = self.cache_collection.find_one({"cache_key": cache_key, "type": "image"})
            if cached and cached.get("ttl", 0) > datetime.utcnow().timestamp():
                return cached.get("url")
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        return None
    
    def _store_cache(self, cache_key: str, url: str, ttl: int = 86400):
        """Store image URL in cache"""
        try:
            self.cache_collection.update_one(
                {"cache_key": cache_key, "type": "image"},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "type": "image",
                        "url": url,
                        "ttl": datetime.utcnow().timestamp() + ttl,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Cache store failed: {e}")
    
    def generate(self,
                 prompt: str,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 negative_prompt: Optional[str] = None,
                 num_images: int = 1,
                 use_cache: bool = True,
                 session_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 caption: bool = False) -> Dict[str, Any]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            negative_prompt: Negative prompt
            num_images: Number of images to generate
            use_cache: Whether to use cache
            session_id: Optional session identifier for logging
            metadata: Additional metadata to store with output
            caption: Whether to auto-caption generated images
        
        Returns:
            Dict with generated image URLs and metadata
        """
        try:
            config = self.model_manager.get_image_model_config()
            width = width or config.get("generation", {}).get("width", 1024)
            height = height or config.get("generation", {}).get("height", 1024)
            
            # Enhance prompt with educational context
            enhanced_prompt = self._enhance_prompt(prompt, config)
            
            # Check cache
            cache_key = self._get_cache_key(enhanced_prompt, width, height)
            if use_cache:
                cached_url = self._check_cache(cache_key)
                if cached_url:
                    return {
                        "success": True,
                        "urls": [cached_url],
                        "cached": True,
                        "model": config.get("name"),
                        "prompt": enhanced_prompt,
                        "generated_at": datetime.utcnow(),
                        "media_ids": [],
                        "captions": []
                    }
            
            # Load model if not already loaded
            if self.image_model is None:
                try:
                    self.image_model = self.model_manager.load_image_model()
                except ImportError as e:
                    return {
                        "success": False,
                        "error": f"AI models not installed: {str(e)}",
                        "urls": []
                    }
            
            # Get pipeline
            pipe = self.image_model["pipe"]
            gen_config = config.get("generation", {})
            
            # Generate images
            urls = []
            media_ids = []
            captions = []
            enhanced_metadata = metadata or {}
            
            for i in range(num_images):
                result = pipe(
                    enhanced_prompt,
                    negative_prompt=negative_prompt or gen_config.get("negative_prompt", ""),
                    width=width,
                    height=height,
                    guidance_scale=gen_config.get("guidance_scale", 7.5),
                    num_inference_steps=gen_config.get("num_inference_steps", 50)
                )
                
                image = result.images[0]
                
                # Save image
                filename = f"{cache_key}_{i}.png"
                filepath = self.output_dir / filename
                image.save(filepath)

                caption_text = None
                if caption:
                    caption_result = self.caption_image(str(filepath))
                    if caption_result.get("success"):
                        caption_text = caption_result.get("caption")
                captions.append(caption_text)

                alt_text = (
                    caption_text or
                    enhanced_metadata.get("alt_text") or
                    enhanced_metadata.get("description") or
                    prompt
                )

                stored_metadata = {
                    **self._safe_for_storage(enhanced_metadata),
                    "caption": caption_text,
                    "cache_key": cache_key,
                    "prompt": enhanced_prompt,
                    "width": width,
                    "height": height
                }
                
                # Store in database
                media_doc = {
                    "url": str(filepath),
                    "alt_text": alt_text,
                    "source": "ai_generated",
                    "type": "image",
                    "linked_slideId": None,
                    "locale": "en",
                    "tags": self._extract_tags(prompt),
                    "generated_by_ai": True,
                    "generation_prompt": enhanced_prompt,
                    "created_at": datetime.utcnow(),
                    "metadata": stored_metadata
                }
                if session_id and ObjectId.is_valid(session_id):
                    media_doc["session_id"] = ObjectId(session_id)
                elif session_id:
                    media_doc["session_id"] = session_id
                
                media_result = self.media_collection.insert_one(media_doc)
                media_id = str(media_result.inserted_id)
                urls.append(str(filepath))
                media_ids.append(media_id)

                self._log_output(
                    session_id=session_id,
                    prompt=enhanced_prompt,
                    file_path=str(filepath),
                    metadata={**stored_metadata, "media_id": media_id}
                )
            
            # Store in cache
            if use_cache and urls:
                self._store_cache(cache_key, urls[0])
            
            return {
                "success": True,
                "urls": urls,
                "cached": False,
                "model": config.get("name"),
                "prompt": enhanced_prompt,
                "generated_at": datetime.utcnow(),
                "media_ids": media_ids,
                "captions": captions
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "urls": []
            }
    
    def _enhance_prompt(self, prompt: str, config: Dict) -> str:
        """Enhance prompt with educational context"""
        context_prompts = config.get("context_prompts", {})
        
        enhanced = prompt
        
        # Add style
        if context_prompts.get("style"):
            enhanced += f", {context_prompts['style']}"
        
        # Add audience context
        if context_prompts.get("audience"):
            enhanced += f", suitable for {context_prompts['audience']}"
        
        # Add quality
        if context_prompts.get("quality"):
            enhanced += f", {context_prompts['quality']}"
        
        return enhanced
    
    def _extract_tags(self, prompt: str) -> List[str]:
        """Extract tags from prompt for searchability"""
        # Simple tag extraction
        tags = []
        keywords = ["educational", "classroom", "student", "teacher", "diagram", "illustration", "chart", "graph"]
        prompt_lower = prompt.lower()
        for keyword in keywords:
            if keyword in prompt_lower:
                tags.append(keyword)
        return tags
    
    def _safe_for_storage(self, payload: Any) -> Any:
        """Ensure payload is serializable for MongoDB storage"""
        if isinstance(payload, dict):
            return {str(key): self._safe_for_storage(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._safe_for_storage(item) for item in payload]
        if isinstance(payload, tuple):
            return [self._safe_for_storage(item) for item in payload]
        if isinstance(payload, datetime):
            return payload
        if isinstance(payload, (str, int, float, bool)) or payload is None:
            return payload
        try:
            json.dumps(payload)
            return payload
        except TypeError:
            return str(payload)
    
    def _log_output(self,
                    session_id: Optional[str],
                    prompt: str,
                    file_path: str,
                    metadata: Optional[Dict[str, Any]] = None):
        """Log generated image output to analytics collection"""
        try:
            doc = {
                "type": "image",
                "prompt": prompt,
                "file_path": file_path,
                "created_at": datetime.utcnow(),
                "metadata": self._safe_for_storage(metadata or {}),
                "model": self.model_manager.get_image_model_config().get("name")
            }
            if session_id and ObjectId.is_valid(session_id):
                doc["session_id"] = ObjectId(session_id)
            elif session_id:
                doc["session_id"] = session_id
            self.outputs_collection.insert_one(doc)
        except Exception as e:
            logger.warning(f"Failed to log image output: {e}")
    
    def _build_marker_prompt(self,
                             description: str,
                             marker: Dict[str, Any],
                             context: Dict[str, Any]) -> str:
        """Construct a Stable Diffusion prompt from marker metadata"""
        prompt_parts = [f"Educational illustration showing {description}"]
        
        slide_title = marker.get("slide_title")
        if slide_title:
            prompt_parts.append(f"supporting slide titled '{slide_title}'")
        
        subject = context.get("subject")
        if subject:
            prompt_parts.append(f"focused on {subject}")
        
        grade_level = context.get("grade_level")
        if grade_level:
            prompt_parts.append(f"appropriate for {grade_level} students")
        
        locale = context.get("locale")
        if locale:
            prompt_parts.append(f"in {locale} language context")
        
        placement = (marker.get("placement") or "").lower()
        if placement == "right":
            prompt_parts.append("composition balanced with main subject on right side")
        elif placement == "left":
            prompt_parts.append("composition balanced with main subject on left side")
        elif placement in {"hero", "full"}:
            prompt_parts.append("wide hero illustration spanning the slide")
        
        prompt_parts.append("clear labels, classroom friendly, diverse representation, high quality concept art")
        return ", ".join(filter(None, prompt_parts))
    
    def generate_from_markers(self,
                              markers: List[Dict[str, Any]],
                              session_id: Optional[str] = None,
                              context: Optional[Dict[str, Any]] = None,
                              caption: bool = True) -> Dict[str, Any]:
        """Generate images based on LLM-provided image markers"""
        if not markers:
            return {"success": True, "items": [], "errors": []}
        
        context = context or {}
        config = self.model_manager.get_image_model_config()
        gen_defaults = config.get("generation", {})
        
        items: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        
        for marker in markers:
            description = marker.get("description") or marker.get("alt_text")
            marker_text = marker.get("marker")
            if not description and isinstance(marker_text, str):
                if ":" in marker_text:
                    description = marker_text.split(":", 1)[1].strip(" ]")
                else:
                    description = marker_text.strip("[]")
            if not description:
                errors.append({**marker, "error": "No description available for marker"})
                continue
            
            base_prompt = self._build_marker_prompt(description, marker, context)
            
            width = marker.get("width") or context.get("image_width") or gen_defaults.get("width", 1024)
            height = marker.get("height") or context.get("image_height") or gen_defaults.get("height", 768)
            
            metadata = {
                "marker": marker,
                "description": description,
                "placement": marker.get("placement"),
                "slide_title": marker.get("slide_title"),
                "alt_text": marker.get("alt_text") or description,
                "context": context
            }
            
            result = self.generate(
                prompt=base_prompt,
                width=width,
                height=height,
                negative_prompt=context.get("negative_prompt"),
                num_images=1,
                use_cache=True,
                session_id=session_id,
                metadata=metadata,
                caption=caption
            )
            
            if not result.get("success"):
                errors.append({**marker, "error": result.get("error", "Image generation failed")})
                continue
            
            url = result.get("urls", [None])[0]
            media_id = result.get("media_ids", [None])[0]
            caption_text = result.get("captions", [None])[0]
            
            items.append({
                "marker": marker,
                "prompt": base_prompt,
                "url": url,
                "media_id": media_id,
                "caption": caption_text,
                "generated_at": result.get("generated_at")
            })
        
        return {
            "success": len(errors) == 0,
            "items": items,
            "errors": errors
        }
    
    def generate_for_slide(self,
                          slide_title: str,
                          slide_content: List[str],
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate image appropriate for a slide"""
        # Create prompt from slide content
        content_summary = " ".join(slide_content[:3])  # Use first 3 bullets
        prompt = f"Educational illustration for: {slide_title}. {content_summary}"
        
        # Adjust for audience
        if context:
            if context.get("grade_level"):
                prompt += f", appropriate for {context['grade_level']} students"
            if context.get("subject"):
                prompt += f", {context['subject']} subject"
        
        session_id = None
        if context:
            session_id = context.get("text_session_id") or context.get("session_id")
        metadata = {
            "slide_title": slide_title,
            "source": "slide_content",
            "context": context or {},
            "alt_text": f"{slide_title} illustration"
        }
        
        return self.generate(
            prompt,
            width=1024,
            height=768,
            session_id=session_id,
            metadata=metadata,
            caption=(context or {}).get("auto_caption", True)
        )
    
    def generate_diagram_image(self,
                              diagram_description: str,
                              diagram_type: str = "process") -> Dict[str, Any]:
        """Generate diagram-style image"""
        prompt = f"Educational {diagram_type} diagram: {diagram_description}, clear labels, professional diagram style"
        return self.generate(prompt, width=1024, height=1024)
    
    def caption_image(self, image_path: str) -> Dict[str, Any]:
        """Generate caption for an image using vision model"""
        try:
            if self.vision_model is None:
                try:
                    self.vision_model = self.model_manager.load_vision_model()
                except ImportError as e:
                    return {
                        "success": False,
                        "error": f"Vision models not installed: {str(e)}",
                        "caption": ""
                    }
            
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Get processor and model
            processor = self.vision_model["processor"]
            model = self.vision_model["model"]
            
            # Generate caption
            inputs = processor(image, return_tensors="pt")
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            out = model.generate(**inputs, max_length=50)
            caption = processor.decode(out[0], skip_special_tokens=True)
            
            return {
                "success": True,
                "caption": caption
            }
            
        except Exception as e:
            logger.error(f"Image captioning failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "caption": ""
            }

