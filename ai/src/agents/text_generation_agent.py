"""
Text Generation Agent: Uses Hugging Face LLMs for content generation
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from bson import ObjectId

# Lazy import for torch
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

from agents.model_manager import get_model_manager
from ai_db import get_ai_db

logger = logging.getLogger(__name__)


class TextGenerationAgent:
    """Agent that generates text content using Hugging Face LLMs"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.cache_collection = self.db["ai_cache"]
        self.feedback_collection = self.db["ai_feedback"]
        self.sessions_collection = self.db["ai_sessions"]
        self.outputs_collection = self.db["ai_outputs"]
        self.model_manager = get_model_manager()
        self.text_model = None
        self._ensure_model_loaded()
    
    def _ensure_model_loaded(self):
        """Ensure text model is loaded (lazy loading)"""
        # Don't load model on init - only when actually needed
        pass
    
    def _get_cache_key(self, prompt: str, context: Dict = None) -> str:
        """Generate cache key for prompt"""
        context_str = json.dumps(context, sort_keys=True) if context else "{}"
        cache_data = f"{prompt}_{context_str}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check if result exists in cache"""
        try:
            cached = self.cache_collection.find_one({"cache_key": cache_key})
            if cached and cached.get("ttl", 0) > datetime.utcnow().timestamp():
                return {
                    "text": cached.get("result", ""),
                    "metadata": cached.get("metadata", {})
                }
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        return None
    
    def _store_cache(self, 
                     cache_key: str, 
                     result: str, 
                     metadata: Optional[Dict[str, Any]] = None,
                     ttl: int = 3600):
        """Store result in cache"""
        try:
            self.cache_collection.update_one(
                {"cache_key": cache_key},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "result": result,
                        "metadata": self._safe_for_storage(metadata or {}),
                        "ttl": datetime.utcnow().timestamp() + ttl,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Cache store failed: {e}")
    
    def _start_session(self, prompt: str, context: Optional[Dict[str, Any]]) -> Optional[str]:
        """Log the start of a generation session"""
        try:
            session_doc = {
                "prompt": prompt,
                "context": self._safe_for_storage(context or {}),
                "model": self.model_manager.get_text_model_config().get("name"),
                "status": "processing",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.sessions_collection.insert_one(session_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.warning(f"Failed to log session start: {e}")
            return None
    
    def _finalize_session(self,
                          session_id: Optional[str],
                          status: str,
                          success: bool,
                          metadata: Optional[Dict[str, Any]] = None):
        """Finalize session log"""
        if not session_id:
            return
        try:
            if not ObjectId.is_valid(session_id):
                return
            update_doc = {
                "status": status,
                "success": success,
                "updated_at": datetime.utcnow()
            }
            if metadata:
                update_doc["metadata"] = self._safe_for_storage(metadata)
            self.sessions_collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": update_doc}
            )
        except Exception as e:
            logger.warning(f"Failed to finalize session: {e}")
    
    def _log_output(self,
                    session_id: Optional[str],
                    prompt: str,
                    generated_text: str,
                    metadata: Optional[Dict[str, Any]] = None):
        """Store generation output for auditing and analytics"""
        try:
            doc = {
                "session_id": ObjectId(session_id) if session_id and ObjectId.is_valid(session_id) else session_id,
                "prompt": prompt,
                "generated_text": generated_text,
                "metadata": self._safe_for_storage(metadata or {}),
                "model": self.model_manager.get_text_model_config().get("name"),
                "created_at": datetime.utcnow()
            }
            self.outputs_collection.insert_one(doc)
        except Exception as e:
            logger.warning(f"Failed to log generation output: {e}")
    
    def _extract_image_markers(self, text: str) -> List[Dict[str, Any]]:
        """Extract image markers (e.g., [IMAGE:diagram]) from generated text"""
        markers: List[Dict[str, Any]] = []
        pattern = r"\[(IMAGE(?:_[A-Z]+)?):([^\]]+)\]"
        for match in re.finditer(pattern, text):
            markers.append({
                "marker": match.group(0),
                "token": match.group(1),
                "description": match.group(2).strip(),
                "start": match.start(),
                "end": match.end()
            })
        return markers
    
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
    
    def generate(self, 
                 prompt: str,
                 context: Optional[Dict] = None,
                 max_length: Optional[int] = None,
                 temperature: Optional[float] = None,
                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate text using LLM
        
        Args:
            prompt: Input prompt
            context: Additional context
            max_length: Maximum generation length
            temperature: Sampling temperature
            use_cache: Whether to use cache
        
        Returns:
            Dict with generated text and metadata
        """
        session_id = self._start_session(prompt, context)
        start_time = datetime.utcnow()
        cache_key: Optional[str] = None
        context = context or {}
        
        try:
            # Check cache
            cache_key = self._get_cache_key(prompt, context)
            if use_cache:
                cached_result = self._check_cache(cache_key)
                if cached_result:
                    cache_metadata = cached_result.get("metadata", {})
                    image_markers = cache_metadata.get("image_markers", [])
                    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                    session_metadata = {
                        **cache_metadata,
                        "from_cache": True,
                        "cache_key": cache_key,
                        "duration_ms": duration_ms
                    }
                    self._log_output(
                        session_id,
                        prompt,
                        cached_result.get("text", ""),
                        metadata=session_metadata
                    )
                    self._finalize_session(
                        session_id,
                        status="completed",
                        success=True,
                        metadata=session_metadata
                    )
                    return {
                        "success": True,
                        "text": cached_result.get("text", ""),
                        "cached": True,
                        "model": self.model_manager.get_text_model_config().get("name"),
                        "prompt": prompt,
                        "generated_at": cache_metadata.get("generated_at", datetime.utcnow()),
                        "session_id": session_id,
                        "image_markers": image_markers,
                        "metadata": session_metadata
                    }
            
            # Prepare prompt
            formatted_prompt = self._format_prompt(prompt, context)
            
            # Load model if not already loaded
            if self.text_model is None:
                try:
                    self.text_model = self.model_manager.load_text_model()  
                except ImportError as e:
                    failure_metadata = {
                        "error": f"AI models not installed: {str(e)}",
                        "cache_key": cache_key,
                        "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                    }
                    self._finalize_session(
                        session_id,
                        status="failed",
                        success=False,
                        metadata=failure_metadata
                    )
                    return {
                        "success": False,
                        "error": f"AI models not installed: {str(e)}",
                        "text": ""
                    }
            
            # Get model and tokenizer
            model_data = self.text_model
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]
            config = model_data["config"]
            
            # Tokenize
            inputs = tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=config.get("max_length", 2048)
            )
            
            # Move to device
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            generation_config = {
                "max_new_tokens": max_length or config.get("max_new_tokens", 512),
                "temperature": temperature or config.get("temperature", 0.7),
                "top_p": config.get("top_p", 0.9),
                "top_k": config.get("top_k", 50),
                "repetition_penalty": config.get("repetition_penalty", 1.1),
                "do_sample": True,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            if HAS_TORCH:
                with torch.no_grad():
                    outputs = model.generate(**inputs, **generation_config)
            else:
                outputs = model.generate(**inputs, **generation_config)
            
            # Decode
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove input prompt from output
            if generated_text.startswith(formatted_prompt):
                generated_text = generated_text[len(formatted_prompt):].strip()
            
            # Extract metadata
            image_markers = self._extract_image_markers(generated_text)
            generation_metadata = {
                "image_markers": image_markers,
                "cache_key": cache_key,
                "generated_at": datetime.utcnow(),
                "from_cache": False,
                "context": context,
                "model": {
                    "name": config.get("name"),
                    "max_new_tokens": generation_config["max_new_tokens"],
                    "temperature": generation_config["temperature"],
                    "top_p": generation_config["top_p"],
                    "top_k": generation_config["top_k"],
                    "repetition_penalty": generation_config["repetition_penalty"]
                },
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            
            # Store in cache
            if use_cache:
                self._store_cache(cache_key, generated_text, metadata=generation_metadata)
            
            # Log output and finalize session
            self._log_output(session_id, prompt, generated_text, metadata=generation_metadata)
            self._finalize_session(
                session_id,
                status="completed",
                success=True,
                metadata=generation_metadata
            )
            
            return {
                "success": True,
                "text": generated_text,
                "cached": False,
                "model": config.get("name"),
                "prompt": prompt,
                "generated_at": generation_metadata["generated_at"],
                "session_id": session_id,
                "image_markers": image_markers,
                "metadata": generation_metadata
            }
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            failure_metadata = {
                "error": str(e),
                "cache_key": cache_key,
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            self._finalize_session(
                session_id,
                status="failed",
                success=False,
                metadata=failure_metadata
            )
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def _format_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Format prompt with context for LLM"""
        if context is None:
            context = {}
        
        # Build system prompt
        system_prompt = "You are an expert educational content creator. Generate high-quality, accurate, and engaging educational content."
        
        # Add context
        if context.get("grade_level"):
            system_prompt += f"\nTarget audience: {context['grade_level']} students."
        if context.get("subject"):
            system_prompt += f"\nSubject: {context['subject']}."
        if context.get("locale"):
            system_prompt += f"\nLanguage: {context['locale']}."
        if context.get("difficulty"):
            system_prompt += f"\nDifficulty level: {context['difficulty']}."
        
        # Format based on model
        config = self.model_manager.get_text_model_config()
        model_name = config.get("name", "")
        
        if "llama" in model_name.lower():
            # Llama format
            return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
        elif "mistral" in model_name.lower():
            # Mistral format
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "falcon" in model_name.lower():
            # Falcon format
            return f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        else:
            # Default format
            return f"{system_prompt}\n\n{prompt}\n\nResponse:"
    
    def generate_slides_content(self, 
                                topic: str,
                                num_slides: int = 5,
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate slide content for a topic"""
        prompt = f"""Create a comprehensive educational presentation on "{topic}".

Requirements:
- Create {num_slides} slides
- Each slide should have a clear title and 3-5 bullet points
- Content should be educational, accurate, and engaging
- Include examples and key concepts
- Insert at least one inline image marker per slide using [IMAGE:description] or [IMAGE_RIGHT:description] to indicate where diagrams/visuals should appear
- Provide alt text suggestions and placement hints for each image marker

Format your response as JSON:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "title": "Slide Title",
      "bullets": ["Point 1", "Point 2", "Point 3"],
      "key_points": ["Key point 1", "Key point 2"],
      "examples": ["Example 1", "Example 2"],
      "images": [
        {{
          "marker": "[IMAGE_RIGHT: diagram of photosynthesis]",
          "placement": "right",
          "alt_text": "Diagram showing the photosynthesis process"
        }}
      ]
    }}
  ]
}}"""
        
        result = self.generate(prompt, context, max_length=2048)
        
        if result["success"]:
            # Try to parse JSON from response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                    result["content"] = content
                    aggregated_markers = list(result.get("image_markers", []))
                    for slide in content.get("slides", []):
                        for image in slide.get("images", []):
                            aggregated_markers.append({
                                "marker": image.get("marker"),
                                "description": image.get("alt_text") or image.get("marker"),
                                "placement": image.get("placement", "auto"),
                                "slide_title": slide.get("title")
                            })
                    result["image_markers"] = aggregated_markers
            except Exception as e:
                logger.warning(f"Failed to parse JSON from response: {e}")
                # Fallback: structure the text manually
                fallback_content = self._parse_text_to_slides(result["text"], topic, num_slides)
                result["content"] = fallback_content
                fallback_markers = list(result.get("image_markers", []))
                for slide in fallback_content.get("slides", []):
                    for image in slide.get("images", []):
                        fallback_markers.append({
                            "marker": image.get("marker"),
                            "description": image.get("alt_text"),
                            "placement": image.get("placement", "auto"),
                            "slide_title": slide.get("title")
                        })
                result["image_markers"] = fallback_markers
        
        return result
    
    def generate_quiz_questions(self,
                                topic: str,
                                num_questions: int = 5,
                                question_type: str = "mcq",
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate quiz questions for a topic"""
        prompt = f"""Create {num_questions} {question_type.upper()} questions about "{topic}".

Requirements:
- Questions should test understanding of key concepts
- Include correct answers and explanations
- Difficulty appropriate for the audience

Format your response as JSON:
{{
  "questions": [
    {{
      "question": "Question text",
      "type": "{question_type}",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Explanation of the answer"
    }}
  ]
}}"""
        
        result = self.generate(prompt, context, max_length=1024)
        
        if result["success"]:
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                    result["questions"] = content.get("questions", [])
            except Exception as e:
                logger.warning(f"Failed to parse JSON from response: {e}")
        
        return result
    
    def generate_speaker_notes(self,
                               slide_title: str,
                               slide_content: List[str],
                               context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate speaker notes for a slide"""
        content_text = "\n".join([f"- {point}" for point in slide_content])
        
        prompt = f"""Create detailed speaker notes for this slide:

Title: {slide_title}

Content:
{content_text}

Generate:
- Main talking points
- Examples to mention
- Transitions to next slide
- Audience engagement questions

Format as JSON:
{{
  "main_points": ["Point 1", "Point 2"],
  "talking_points": ["Talking point 1", "Talking point 2"],
  "examples": ["Example 1", "Example 2"],
  "transitions": ["Transition phrase"],
  "engagement": ["Question 1", "Question 2"]
}}"""
        
        result = self.generate(prompt, context, max_length=512)
        
        if result["success"]:
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                    result["notes"] = content
            except Exception as e:
                logger.warning(f"Failed to parse JSON from response: {e}")
        
        return result
    
    def _parse_text_to_slides(self, text: str, topic: str, num_slides: int) -> Dict:
        """Fallback: Parse plain text into slide structure"""
        # Simple text parsing as fallback
        lines = text.split('\n')
        slides = []
        current_slide = None
        image_pattern = re.compile(r"\[(IMAGE(?:_[A-Z]+)?):([^\]]+)\]")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            images_in_line = image_pattern.findall(line)
            cleaned_line = image_pattern.sub('', line).strip()
            
            # Detect slide titles (lines that look like titles)
            if cleaned_line and len(cleaned_line) < 100 and not cleaned_line.startswith('-'):
                if current_slide:
                    slides.append(current_slide)
                current_slide = {
                    "title": cleaned_line,
                    "bullets": [],
                    "key_points": [],
                    "examples": [],
                    "images": []
                }
            elif current_slide and line.startswith('-'):
                if cleaned_line.startswith('-'):
                    cleaned_line = cleaned_line[1:].strip()
                if cleaned_line:
                    current_slide["bullets"].append(cleaned_line)
            elif current_slide and cleaned_line:
                current_slide["bullets"].append(cleaned_line)
            
            if current_slide and images_in_line:
                for marker, description in images_in_line:
                    current_slide.setdefault("images", []).append({
                        "marker": f"[{marker}:{description.strip()}]",
                        "placement": "auto",
                        "alt_text": description.strip()
                    })
        
        if current_slide:
            slides.append(current_slide)
        
        # Ensure we have the right number of slides
        while len(slides) < num_slides:
            slides.append({
                "title": f"{topic} - Slide {len(slides) + 1}",
                "bullets": ["Key concept", "Important point", "Example"],
                "key_points": [],
                "examples": [],
                "images": []
            })
        
        return {
            "title": f"{topic} Presentation",
            "slides": slides[:num_slides]
        }
    
    def store_feedback(self, 
                      prompt: str,
                      generated_text: str,
                      rating: int,
                      feedback: Optional[str] = None,
                      user_id: Optional[str] = None):
        """Store user feedback for model improvement"""
        try:
            self.feedback_collection.insert_one({
                "prompt": prompt,
                "generated_text": generated_text,
                "rating": rating,
                "feedback": feedback,
                "user_id": user_id,
                "model": self.model_manager.get_text_model_config().get("name"),
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            logger.warning(f"Failed to store feedback: {e}")

