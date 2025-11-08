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

from agents.model_manager import get_model_manager
from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class ImageGenerationAgent:
    """Agent that generates educational images using Stable Diffusion"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.media_collection = self.db["media"]
        self.cache_collection = self.db["ai_cache"]
        self.model_manager = get_model_manager()
        self.image_model = None
        self.vision_model = None
        self._ensure_models_loaded()
        self.output_dir = Path("out/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _ensure_models_loaded(self):
        """Ensure image models are loaded"""
        if self.image_model is None:
            self.image_model = self.model_manager.load_image_model()
        # Vision model loaded on demand
    
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
                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            negative_prompt: Negative prompt
            num_images: Number of images to generate
            use_cache: Whether to use cache
        
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
                        "model": config.get("name")
                    }
            
            # Get pipeline
            pipe = self.image_model["pipe"]
            gen_config = config.get("generation", {})
            
            # Generate images
            images = []
            urls = []
            
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
                images.append(image)
                
                # Save image
                filename = f"{cache_key}_{i}.png"
                filepath = self.output_dir / filename
                image.save(filepath)
                
                # Store in database
                media_doc = {
                    "url": str(filepath),
                    "alt_text": prompt,
                    "source": "ai_generated",
                    "type": "image",
                    "linked_slideId": None,
                    "locale": "en",
                    "tags": self._extract_tags(prompt),
                    "generated_by_ai": True,
                    "generation_prompt": enhanced_prompt,
                    "created_at": datetime.utcnow()
                }
                
                result = self.media_collection.insert_one(media_doc)
                media_id = str(result.inserted_id)
                urls.append(str(filepath))
            
            # Store in cache
            if use_cache and urls:
                self._store_cache(cache_key, urls[0])
            
            return {
                "success": True,
                "urls": urls,
                "cached": False,
                "model": config.get("name"),
                "prompt": enhanced_prompt,
                "generated_at": datetime.utcnow()
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
        
        return self.generate(prompt, width=1024, height=768)
    
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
                self.vision_model = self.model_manager.load_vision_model()
            
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

