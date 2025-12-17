"""
Text Generation Agent: Uses Google Gemini API for content generation
"""

import logging
import json
import re
import requests
import time
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

# Import config module (file) - use importlib to avoid directory conflict
import importlib.util
from pathlib import Path
config_file = Path(__file__).parent.parent / "config.py"
spec = importlib.util.spec_from_file_location("ai_config", config_file)
ai_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_config)
get_config = ai_config.get_config

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
            
            # Check which provider to use
            config_obj = get_config()
            text_config = self.model_manager.get_text_model_config()
            provider = text_config.get("provider", config_obj.llm_provider)
            use_api = text_config.get("use_api", True)
            
            # Route to appropriate API based on provider
            if provider == "ollama":
                api_result = self._generate_via_ollama_api(
                    formatted_prompt,
                    max_length=max_length,
                    temperature=temperature,
                    config=text_config
                )
            elif provider == "gemini" or provider is None:
                # Use Gemini API
                if not config_obj.gemini_api_key:
                    failure_metadata = {
                        "error": "GEMINI_API_KEY is not set. Add it to ai/.env file. Get your key from: https://aistudio.google.com/app/apikey",
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
                        "error": "GEMINI_API_KEY is not set. Add it to ai/.env file. Get your key from: https://aistudio.google.com/app/apikey",
                        "text": ""
                    }
                
                api_result = self._generate_via_gemini_api(
                    formatted_prompt,
                    max_length=max_length,
                    temperature=temperature,
                    config=text_config
                )
            elif provider == "local" and not use_api:
                # Use local transformers model (legacy support)
                api_result = self._generate_via_local_model(
                    formatted_prompt,
                    max_length=max_length,
                    temperature=temperature,
                    config=text_config
                )
            else:
                failure_metadata = {
                    "error": f"Unknown provider: {provider}",
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
                    "error": f"Unknown provider: {provider}. Supported providers: gemini, ollama, local",
                    "text": ""
                }
            
            if not api_result.get("success"):
                failure_metadata = {
                    "error": api_result.get("error", "API generation failed"),
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
                    "error": api_result.get("error", "API generation failed"),
                    "text": ""
                }

            generated_text = api_result.get("text", "")
            # Clean markdown formatting
            generated_text = self._clean_markdown_formatting(generated_text)
            
            # Legacy local model loading removed - using Gemini only
            if False:  # This block is disabled - Gemini only
                # Load model locally if not already loaded
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
                    "max_new_tokens": max_length or config.get("max_new_tokens", 2048),
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
            
            # Build model metadata
            config_obj = get_config()
            provider = text_config.get("provider", config_obj.llm_provider)
            if provider == "gemini":
                model_name = config_obj.gemini_model_id or text_config.get("name") or "gemini-flash-lite-latest"
            elif provider == "ollama":
                model_name = text_config.get("ollama_model") or text_config.get("name") or "deepseek-r1:1.5b"
            else:
                model_name = text_config.get("name") or text_config.get("active_model", "unknown")
            gen_config = text_config.get("generation", {})
            
            generation_metadata = {
                "image_markers": image_markers,
                "cache_key": cache_key,
                "generated_at": datetime.utcnow(),
                "from_cache": False,
                "context": context,
                "model": {
                    "name": model_name,
                    "provider": provider,
                    "use_api": text_config.get("use_api", True),
                    "max_new_tokens": max_length or gen_config.get("max_new_tokens", 2048),
                    "temperature": temperature if temperature is not None else gen_config.get("temperature", 0.7),
                    "top_p": gen_config.get("top_p", 0.9),
                    "top_k": gen_config.get("top_k", 50),
                    "repetition_penalty": gen_config.get("repetition_penalty", 1.1)
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
                "model": model_name,
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
    
    def _verify_model_access(self, model_id: str, hf_api_key: str) -> Dict[str, Any]:
        """Verify if model is accessible via HF API"""
        try:
            # Try a simple HEAD request to check if model exists
            response = requests.head(
                f"https://huggingface.co/api/models/{model_id}",
                headers={"Authorization": f"Bearer {hf_api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "message": "Model is accessible"}
            elif response.status_code == 404:
                return {"success": False, "error": f"Model {model_id} not found. Check if the model name is correct."}
            elif response.status_code == 401:
                return {"success": False, "error": "Invalid or missing HF_API_KEY. Check your token."}
            else:
                return {"success": False, "error": f"Model access check failed: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Could not verify model access: {str(e)}"}
    
    def _clean_markdown_formatting(self, text: str) -> str:
        """Remove markdown formatting from text"""
        import re
        if not text:
            return text
        
        # Remove bold markdown (**text** or **text** with spaces)
        text = re.sub(r'\*\*([^*]+?)\*\*', r'\1', text)  # Remove **bold**
        # Remove any remaining standalone **
        text = re.sub(r'\*\*', '', text)
        
        # Remove italic markdown (*text* but not **text**)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\1', text)  # Remove *italic* but not **
        text = re.sub(r'__([^_]+?)__', r'\1', text)  # Remove __bold__
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'\1', text)  # Remove _italic_ but not __
        
        # Remove markdown headers (# ## ###)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown links but keep text [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown code blocks but keep content ```code``` -> code
        text = re.sub(r'```[\w]*\n?([^`]+)\n?```', r'\1', text, flags=re.DOTALL)
        
        # Remove inline code backticks `code` -> code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
        
        return text.strip()
    
    def _generate_via_gemini_api(self,
                                  prompt: str,
                                  max_length: Optional[int] = None,
                                  temperature: Optional[float] = None,
                                  config: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate text using Google Gemini API"""
        config_obj = get_config()
        gemini_api_key = config_obj.gemini_api_key
        # Get model from config or use default
        model_id = config_obj.gemini_model_id or (config.get("name") if config else "gemini-flash-lite-latest")
        
        # Get API version from config (v1 or v1beta)
        api_version = config.get("api_version", "v1") if config else "v1"
        
        # Use model name directly (no mapping needed - use exact names from test results)
        api_model_id = model_id
        
        if not gemini_api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY is not set. Add it to ai/.env file. Get your key from: https://aistudio.google.com/app/apikey",
                "text": ""
            }
        
        # Use config defaults if not provided
        gen_config = config.get("generation", {}) if config else {}
        # Default to 2048 for longer responses, but allow override
        max_tokens = max_length or gen_config.get("max_new_tokens", 2048)
        
        # Ensure minimum reasonable token limit
        if max_tokens < 100:
            max_tokens = 2048
            logger.warning(f"max_tokens too low ({max_length}), using 2048 instead")
        temp = temperature if temperature is not None else gen_config.get("temperature", 0.7)
        
        # Gemini API endpoint - use API version from config
        endpoint_url = f"https://generativelanguage.googleapis.com/{api_version}/models/{api_model_id}:generateContent?key={gemini_api_key}"
        
        logger.info(f"Using Gemini model: {api_model_id} (API: {api_version}, requested: {model_id})")
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temp,
                "topP": gen_config.get("top_p", 0.9),
                "topK": gen_config.get("top_k", 50)
            }
        }
        
        try:
            logger.info(f"Calling Gemini API: {model_id}")
            
            response = requests.post(
                endpoint_url,
                headers={
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=300
            )
            
            if not response.ok:
                error_text = response.text
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                # Check for 404 - model not found, try alternate API version
                if response.status_code == 404 or (error_data.get("error", {}).get("status") == "NOT_FOUND"):
                    # Try alternate API version
                    alternate_version = "v1beta" if api_version == "v1" else "v1"
                    logger.warning(f"Model {api_model_id} not found in {api_version}, trying {alternate_version}")
                    endpoint_url = f"https://generativelanguage.googleapis.com/{alternate_version}/models/{api_model_id}:generateContent?key={gemini_api_key}"
                    response = requests.post(
                        endpoint_url,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=300
                    )
                    if response.ok:
                        api_version = alternate_version
                        logger.info(f"Successfully used {alternate_version} API for {api_model_id}")
                    else:
                        # Try gemma-3-1b-it as final fallback (fastest, most reliable)
                        if api_model_id != "gemma-3-1b-it":
                            logger.warning(f"Model {api_model_id} not found, trying gemma-3-1b-it as fallback")
                            endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-1b-it:generateContent?key={gemini_api_key}"
                            response = requests.post(
                                endpoint_url,
                                headers={"Content-Type": "application/json"},
                                json=payload,
                                timeout=300
                            )
                            if response.ok:
                                api_model_id = "gemma-3-1b-it"
                                api_version = "v1beta"
                                logger.info(f"Successfully using gemma-3-1b-it as fallback")
                    
                    # If still failing, return error
                    if not response.ok:
                        error_text = response.text
                        logger.error(f"Gemini API model not found: {error_text}")
                        return {
                            "success": False,
                            "error": f"Gemini model '{api_model_id}' not found in {api_version}. Try using 'gemma-3-1b-it' in your config. Check available models: https://ai.google.dev/models/gemini",
                            "text": ""
                        }
                
                # Check for quota/resource exhausted errors
                elif response.status_code == 429 or (error_data.get("error", {}).get("status") == "RESOURCE_EXHAUSTED"):
                    # Try gemma-3-1b-it as fallback (fastest, free-tier)
                    if api_model_id != "gemma-3-1b-it":
                        logger.warning(f"Quota exceeded for {api_model_id}, trying gemma-3-1b-it as fallback")
                        endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-1b-it:generateContent?key={gemini_api_key}"
                        response = requests.post(
                            endpoint_url,
                            headers={"Content-Type": "application/json"},
                            json=payload,
                            timeout=300
                        )
                        if response.ok:
                            api_model_id = "gemma-3-1b-it"
                            api_version = "v1beta"
                            logger.info(f"Successfully using gemma-3-1b-it as fallback")
                        else:
                            # Extract retry delay if provided
                            retry_delay = error_data.get("error", {}).get("retryDelay", "30s")
                            logger.error(f"Gemini API quota exceeded. Retry after: {retry_delay}")
                            return {
                                "success": False,
                                "error": f"Gemini API quota exceeded. Please retry in {retry_delay}. Check your quota at: https://ai.google.dev/docs/gemini_api_quotas_and_limits",
                                "text": "",
                                "retry_after": retry_delay
                            }
                    else:
                        # Extract retry delay if provided
                        retry_delay = error_data.get("error", {}).get("retryDelay", "30s")
                        logger.error(f"Gemini API quota exceeded. Retry after: {retry_delay}")
                        return {
                            "success": False,
                            "error": f"Gemini API quota exceeded. Please retry in {retry_delay}. Check your quota at: https://ai.google.dev/docs/gemini_api_quotas_and_limits",
                            "text": "",
                            "retry_after": retry_delay
                        }
                
                # Other errors
                logger.error(f"Gemini API error: {error_text}")
                return {
                    "success": False,
                    "error": f"Gemini API error: {error_text}",
                    "text": ""
                }
            
            result = response.json()
            
            # Log the full response for debugging
            logger.debug(f"Gemini API response: {json.dumps(result, indent=2)}")
            
            # Extract generated text from Gemini response
            generated_text = ""
            
            # Check for error in response
            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                return {
                    "success": False,
                    "error": f"Gemini API error: {error_msg}",
                    "text": ""
                }
            
            # Parse response structure
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                
                # Check for finish reason (might indicate blocking or truncation)
                finish_reason = candidate.get("finishReason", "")
                if finish_reason == "SAFETY":
                    return {
                        "success": False,
                        "error": "Gemini API blocked the response due to safety filters",
                        "text": ""
                    }
                elif finish_reason == "MAX_TOKENS":
                    logger.warning(f"Response was truncated due to max tokens ({max_tokens}). Consider increasing max_new_tokens in config.")
                elif finish_reason == "STOP":
                    # Normal completion
                    pass
                elif finish_reason:
                    logger.info(f"Finish reason: {finish_reason}")
                
                # Extract text from content
                if "content" in candidate:
                    content = candidate["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        # Get text from first part
                        part = content["parts"][0]
                        generated_text = part.get("text", "")
                    elif "text" in content:
                        generated_text = content["text"]
            
            # If still no text, check alternative response formats
            if not generated_text:
                # Try direct text field
                if "text" in result:
                    generated_text = result["text"]
                # Try promptFeedback for errors
                elif "promptFeedback" in result:
                    feedback = result["promptFeedback"]
                    if "blockReason" in feedback:
                        return {
                            "success": False,
                            "error": f"Gemini API blocked the prompt: {feedback.get('blockReason', 'Unknown reason')}",
                            "text": ""
                        }
            
            if not generated_text:
                # Log the full response for debugging
                logger.error(f"Gemini API returned empty response. Full response: {json.dumps(result, indent=2)}")
                return {
                    "success": False,
                    "error": f"Gemini API returned empty response. Response structure: {list(result.keys())}",
                    "text": ""
                }
            
            # Clean markdown formatting from response
            generated_text = self._clean_markdown_formatting(generated_text)
            
            return {
                "success": True,
                "text": generated_text
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request to Gemini API timed out",
                "text": ""
            }
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {
                "success": False,
                "error": f"Gemini API request failed: {str(e)}",
                "text": ""
            }
    
    def _generate_via_ollama_api(self,
                                  prompt: str,
                                  max_length: Optional[int] = None,
                                  temperature: Optional[float] = None,
                                  config: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate text using Ollama API (local)"""
        # Get Ollama configuration
        ollama_model = config.get("ollama_model", "deepseek-r1:1.5b") if config else "deepseek-r1:1.5b"
        ollama_base_url = config.get("ollama_base_url", "http://localhost:11434") if config else "http://localhost:11434"
        
        # Use config defaults if not provided
        gen_config = config.get("generation", {}) if config else {}
        max_tokens = max_length or gen_config.get("max_new_tokens", 2048)
        temp = temperature if temperature is not None else gen_config.get("temperature", 0.7)
        
        # Ollama API endpoint
        endpoint_url = f"{ollama_base_url}/api/generate"
        
        logger.info(f"Using Ollama model: {ollama_model} at {ollama_base_url}")
        
        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temp,
                "top_p": gen_config.get("top_p", 0.9),
                "top_k": gen_config.get("top_k", 50),
                "repeat_penalty": gen_config.get("repetition_penalty", 1.1)
            }
        }
        
        try:
            logger.info(f"Calling Ollama API: {ollama_model}")
            
            response = requests.post(
                endpoint_url,
                headers={
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=300
            )
            
            if not response.ok:
                error_text = response.text
                logger.error(f"Ollama API error: {error_text}")
                return {
                    "success": False,
                    "error": f"Ollama API error (status {response.status_code}): {error_text}",
                    "text": ""
                }
            
            result = response.json()
            
            # Log the full response for debugging
            logger.debug(f"Ollama API response: {json.dumps(result, indent=2)}")
            
            # Extract generated text from Ollama response
            generated_text = result.get("response", "")
            
            if not generated_text:
                logger.error(f"Ollama API returned empty response. Full response: {json.dumps(result, indent=2)}")
                return {
                    "success": False,
                    "error": f"Ollama API returned empty response. Response structure: {list(result.keys())}",
                    "text": ""
                }
            
            # Clean markdown formatting from response
            generated_text = self._clean_markdown_formatting(generated_text)
            
            return {
                "success": True,
                "text": generated_text
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"Could not connect to Ollama at {ollama_base_url}. Make sure Ollama is running. Start it with: ollama serve",
                "text": ""
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request to Ollama API timed out",
                "text": ""
            }
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return {
                "success": False,
                "error": f"Ollama API request failed: {str(e)}",
                "text": ""
            }
    
    def _generate_via_local_model(self,
                                    prompt: str,
                                    max_length: Optional[int] = None,
                                    temperature: Optional[float] = None,
                                    config: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate text using local transformers model"""
        if not HAS_TORCH:
            return {
                "success": False,
                "error": "PyTorch is required for local model generation. Install with: pip install torch",
                "text": ""
            }
        
        # Load model locally if not already loaded
        if self.text_model is None:
            try:
                self.text_model = self.model_manager.load_text_model()
            except ImportError as e:
                return {
                    "success": False,
                    "error": f"AI models not installed: {str(e)}",
                    "text": ""
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to load local model: {str(e)}",
                    "text": ""
                }
        
        # Get model and tokenizer
        model_data = self.text_model
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]
        model_config = model_data["config"]
        
        # Use config defaults if not provided
        gen_config = model_config.get("generation", {})
        max_tokens = max_length or gen_config.get("max_new_tokens", 2048)
        temp = temperature if temperature is not None else gen_config.get("temperature", 0.7)
        
        try:
            # Tokenize
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=model_config.get("max_length", 2048)
            )
            
            # Move to device
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            generation_config = {
                "max_new_tokens": max_tokens,
                "temperature": temp,
                "top_p": gen_config.get("top_p", 0.9),
                "top_k": gen_config.get("top_k", 50),
                "repetition_penalty": gen_config.get("repetition_penalty", 1.1),
                "do_sample": True,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            with torch.no_grad():
                outputs = model.generate(**inputs, **generation_config)
            
            # Decode
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Clean markdown formatting
            generated_text = self._clean_markdown_formatting(generated_text)
            
            return {
                "success": True,
                "text": generated_text
            }
            
        except Exception as e:
            logger.error(f"Local model generation failed: {e}")
            return {
                "success": False,
                "error": f"Local model generation failed: {str(e)}",
                "text": ""
            }
    
    def _generate_via_hf_api(self,
                             prompt: str,
                             max_length: Optional[int] = None,
                             temperature: Optional[float] = None,
                             config: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate text using Hugging Face Inference API"""
        config_obj = get_config()
        hf_api_key = config_obj.hf_api_key
        # Prioritize model from model registry config, then env var, then default
        model_id = (config.get("name") if config else None) or config_obj.hf_model_id or "mistralai/Mistral-7B-Instruct-v0.2"
        
        if not hf_api_key:
            return {
                "success": False,
                "error": "HF_API_KEY is not set. Add it to ai/.env file. Get your token from: https://huggingface.co/settings/tokens",
                "text": ""
            }
        
        # Verify model access first
        verification = self._verify_model_access(model_id, hf_api_key)
        if not verification.get("success"):
            logger.warning(f"Model verification failed: {verification.get('error')}")
            # Try fallback model if v0.3 fails
            if "v0.3" in model_id:
                fallback_model = model_id.replace("v0.3", "v0.2")
                logger.info(f"Trying fallback model: {fallback_model}")
                fallback_verification = self._verify_model_access(fallback_model, hf_api_key)
                if fallback_verification.get("success"):
                    model_id = fallback_model
                    logger.info(f"Using fallback model: {model_id}")
                else:
                    logger.warning(f"Fallback model also failed: {fallback_verification.get('error')}")
        
        # Use config defaults if not provided
        gen_config = config.get("generation", {}) if config else {}
        max_new_tokens = max_length or gen_config.get("max_new_tokens", 2048)
        temp = temperature if temperature is not None else gen_config.get("temperature", 0.7)
        
        # For Mistral and other chat models, use chat/completions format
        # Format: messages array with role and content
        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_new_tokens,
            "temperature": temp,
            "top_p": gen_config.get("top_p", 0.9),
            "top_k": gen_config.get("top_k", 50),
            "repetition_penalty": gen_config.get("repetition_penalty", 1.1)
        }
        
        try:
            # Use the standard Inference API endpoint
            # ENDPOINT: https://api-inference.huggingface.co/models/{model_id}
            endpoint_url = f"https://api-inference.huggingface.co/models/{model_id}"
            
            # For Mistral, use the standard inference API format (not chat/completions)
            api_payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temp,
                    "top_p": gen_config.get("top_p", 0.9),
                    "top_k": gen_config.get("top_k", 50),
                    "repetition_penalty": gen_config.get("repetition_penalty", 1.1),
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            logger.info(f"Calling HF Inference API: {endpoint_url} with model: {model_id}")
            
            response = requests.post(
                endpoint_url,
                headers={
                    "Authorization": f"Bearer {hf_api_key}",
                    "Content-Type": "application/json"
                },
                json=api_payload,
                timeout=300
            )
            
            # If 503, model is loading
            if response.status_code == 503:
                logger.info(f"Model {model_id} is loading, waiting...")
                time.sleep(10)
                response = requests.post(
                    endpoint_url,
                    headers={
                        "Authorization": f"Bearer {hf_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=api_payload,
                    timeout=300
                )
            
            if response is None or not response.ok:
                error_text = response.text if response else "Unknown error"
                status_code = response.status_code if response else "N/A"
                logger.error(f"HF API error ({status_code}): {error_text}")
                
                # Provide helpful error messages
                if status_code == 404:
                    error_msg = (
                        f"Model '{model_id}' not found. Possible issues:\n"
                        f"1. Model name might be incorrect - check: https://huggingface.co/{model_id}\n"
                        f"2. Model might be private - ensure your HF_API_KEY has access\n"
                        f"3. Model might not be available on Inference API\n"
                        f"Try using: mistralai/Mistral-7B-Instruct-v0.2 or another available model"
                    )
                elif status_code == 401:
                    error_msg = (
                        f"Authentication failed. Check your HF_API_KEY:\n"
                        f"1. Get token from: https://huggingface.co/settings/tokens\n"
                        f"2. Ensure token has 'read' or 'inference' scope\n"
                        f"3. Add to .env file: HF_API_KEY=your_token_here"
                    )
                else:
                    error_msg = f"Hugging Face API error ({status_code}): {error_text}"
                
                return {
                    "success": False,
                    "error": error_msg,
                    "text": "",
                    "model": model_id,
                    "status_code": status_code
                }
            
            result = response.json()
            
            # Inference API response format
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                generated_text = str(result)
            
            # Remove prompt if it's included in response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return {
                "success": True,
                "text": generated_text
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request to Hugging Face API timed out",
                "text": ""
            }
        except Exception as e:
            logger.error(f"HF API call failed: {e}")
            return {
                "success": False,
                "error": f"Hugging Face API request failed: {str(e)}",
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
        elif "mistral" in model_name.lower() or "zephyr" in model_name.lower():
            # Mistral/Zephyr format
            return f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        elif "phi" in model_name.lower():
            # Phi-3 format
            return f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>"
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
        """Generate slide content based on the ACTUAL USER PROMPT, not just subject category"""
        # Get the actual user prompt - this is what the user wants, not a generic subject
        user_prompt = context.get("user_prompt") if context else topic
        subject_category = context.get("subject_category", "") if context else ""
        
        # Build prompt that emphasizes the ACTUAL user request
        prompt = f"""You are a slide generator. For each slide produce a JSON object ONLY.
Do NOT include explanations, markdown, or code fences — return valid JSON. All textual content you emit will be placed directly in the PPT slide title, bullet body, or speaker notes, so never describe placement instructions—just supply the final text itself. Each bullet must be meaningful text that can stand alone on a slide (no placeholders like "Topic 2").

CRITICAL: Generate slides based on the ACTUAL USER REQUEST below. Do NOT generate generic slides about a subject category. 
Focus on what the user specifically asked for.

OUTPUT SCHEMA (exact):
{{
  "slides": [
    {{
      "title": "<string, max 100 chars>",
      "bullets": ["<string, max 12 words>", "..."],
      "notes": "<string, optional speaker notes>",
      "images": [
        {{"id": "<string optional id>", "caption": "<string optional descriptive text>"}}
      ]
    }}
  ]
}}

USER'S ACTUAL REQUEST (generate slides for THIS, not a generic subject):
"{user_prompt}"

{f"Subject category (for context only, NOT the topic): {subject_category}" if subject_category else ""}

TASK:
Create a slide deck of {num_slides} slides based on the USER'S ACTUAL REQUEST above.
Generate content that directly addresses what the user asked for, not generic content about a subject category.
For each slide, output 'title', between 1 and 6 short 'bullets' (each max 12 words)
and optional 'notes'. If an image is suggested, add an entry in 'images' (id or description).
Keep language concise and avoid tokens like "Notes:", "```json", "{{", "}}".
Return only valid JSON matching the schema above."""
        
        # Increase max_length to prevent truncation - expanded content needs more space
        result = self.generate(prompt, context, max_length=8192)
        
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
    
    def expand_slide_content_gemini(self,
                                     slide_json_text: str,
                                     context: Optional[Dict] = None,
                                     max_length: int = 8192) -> Dict[str, Any]:
        """
        Re-run slide JSON through Gemini to expand and enrich the textual content.
        This is the second pass (after initial generation) to make content more detailed.
        """
        prompt = f"""You will receive an existing slide deck as JSON. The content needs to be expanded and enriched.

CRITICAL INSTRUCTIONS:
- Expand ONLY the textual fields (titles, bullets, notes) with MORE DETAIL and DEPTH
- Keep the exact JSON structure (same slides, same keys, same number of bullets and images)
- Expand each bullet into a clear, detailed sentence (40-60 words). Keep the same number of bullets.
- Expand titles to be more descriptive (up to 120 characters) while keeping them concise
- If a slide has "notes", expand to 150-250 words of comprehensive speaker notes
- CRITICAL: Preserve ALL image placeholders exactly as they are. Do NOT modify, add, or remove any entries in the "images" array
- Do not add new slides, fields, or images
- Return ONLY valid JSON. No markdown, no prose outside the JSON

Existing slide JSON:
{slide_json_text}
"""
        # Use Gemini for this expansion pass
        result = self.generate(prompt, context, max_length=max_length)
        
        if result.get("success"):
            try:
                # Parse original JSON to preserve image placeholders
                original_content = None
                try:
                    original_json_match = re.search(r'\{.*\}', slide_json_text, re.DOTALL)
                    if original_json_match:
                        original_content = json.loads(original_json_match.group())
                except Exception:
                    pass
                
                # Parse expanded JSON
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                    
                    # Preserve image placeholders from original (only if both slides are dicts)
                    if original_content:
                        original_slides = original_content.get("slides", []) if isinstance(original_content, dict) else []
                        expanded_slides = content.get("slides", []) if isinstance(content, dict) else []
                        if isinstance(original_slides, list) and isinstance(expanded_slides, list):
                            for idx, (original_slide, expanded_slide) in enumerate(zip(original_slides, expanded_slides)):
                                if not isinstance(original_slide, dict) or not isinstance(expanded_slide, dict):
                                    continue
                                if original_slide.get("images"):
                                    expanded_slide["images"] = original_slide["images"]
                    
                    result["content"] = content
                    result["text"] = json.dumps(content, indent=2)
                    
                    # Preserve image markers
                    aggregated_markers = list(result.get("image_markers", []))
                    slides_list = content.get("slides", []) if isinstance(content, dict) else []
                    if isinstance(slides_list, list):
                        for slide in slides_list:
                            if not isinstance(slide, dict):
                                continue
                            for image in slide.get("images", []) or []:
                                if not isinstance(image, dict):
                                    continue
                                aggregated_markers.append({
                                    "marker": image.get("marker") or image.get("id"),
                                    "description": image.get("caption") or image.get("alt_text") or image.get("marker") or image.get("id"),
                                    "placement": image.get("placement", "auto"),
                                    "slide_title": slide.get("title")
                                })
                    result["image_markers"] = aggregated_markers
            except Exception as e:
                logger.warning(f"Failed to parse Gemini expanded slide JSON: {e}")
        
        return result
    
    def expand_slide_content(self,
                             slide_json_text: str,
                             context: Optional[Dict] = None,
                             max_length: int = 8192) -> Dict[str, Any]:
        """
        Re-run slide JSON through deepseek-r1:1.5b (Ollama) to further enlarge and elaborate the textual content.
        This is the third pass (after Gemini expansion) to add final detail and make it PPT-ready.
        The structure and slide count must remain the same; only enrich bullet text and notes. Image placeholders are preserved.
        """
        prompt = f"""You will receive an existing slide deck as JSON that has already been expanded twice (once through Gemini). 
This is the FINAL expansion pass - make the content RICH, DETAILED, and COMPREHENSIVE for PPT slides.

CRITICAL INSTRUCTIONS:
- This is the THIRD pass - content should be VERY detailed and comprehensive
- Expand ONLY the textual fields (titles, bullets, notes) with MAXIMUM detail and depth
- Keep the exact JSON structure (same slides, same keys, same number of bullets and images)
- Expand each bullet into a comprehensive, detailed sentence (50-80 words). Keep the same number of bullets.
- Make bullets informative, educational, and suitable for presentation slides
- Expand titles to be descriptive and informative (up to 120 characters)
- If a slide has "notes", expand to 200-300 words of comprehensive speaker notes
- CRITICAL: Preserve ALL image placeholders exactly as they are. Do NOT modify, add, or remove any entries in the "images" array
- Do not add new slides, fields, or images
- Return ONLY valid JSON. No markdown, no prose outside the JSON

Existing slide JSON:
{slide_json_text}
"""
        # Use deepseek-r1:1.5b (Ollama) for content expansion
        # Get the deepseek model config from registry
        deepseek_config = None
        for model in self.model_manager.model_registry.get("models", {}).get("text", {}).get("available_models", []):
            if model.get("name") == "deepseek-r1:1.5b":
                deepseek_config = model.copy()
                # Merge with generation settings
                gen_settings = self.model_manager.model_registry.get("models", {}).get("text", {}).get("generation", {})
                deepseek_config.update(gen_settings)
                break
        
        # Fallback to default deepseek config if not found in registry
        if not deepseek_config:
            deepseek_config = {
                "provider": "ollama",
                "ollama_model": "deepseek-r1:1.5b",
                "ollama_base_url": "http://localhost:11434",
                "generation": {
                    "temperature": 0.7,
                    "max_new_tokens": max_length or 4096,
                    "top_p": 0.9,
                    "top_k": 50,
                    "repetition_penalty": 1.1
                }
            }
        
        # Format prompt with context if needed
        formatted_prompt = self._format_prompt(prompt, context)
        
        # Call Ollama API directly with deepseek model
        result = self._generate_via_ollama_api(
            formatted_prompt,
            max_length=max_length,
            temperature=deepseek_config.get("generation", {}).get("temperature", 0.7),
            config=deepseek_config
        )

        if result.get("success"):
            try:
                # Parse original JSON to preserve image placeholders
                original_content = None
                try:
                    original_json_match = re.search(r'\{.*\}', slide_json_text, re.DOTALL)
                    if original_json_match:
                        original_content = json.loads(original_json_match.group())
                except Exception:
                    pass
                
                # Parse expanded JSON
                json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                    
                    # Preserve image placeholders from original if missing in expanded version
                    if original_content:
                        original_slides = original_content.get("slides", [])
                        expanded_slides = content.get("slides", [])
                        for idx, (original_slide, expanded_slide) in enumerate(zip(original_slides, expanded_slides)):
                            # If expanded slide has no images or empty images array, restore from original
                            if not expanded_slide.get("images") or len(expanded_slide.get("images", [])) == 0:
                                if original_slide.get("images"):
                                    expanded_slide["images"] = original_slide["images"]
                            # Otherwise, ensure all original image fields are preserved
                            elif original_slide.get("images"):
                                # Merge: keep expanded images but ensure original structure is maintained
                                original_images = original_slide.get("images", [])
                                expanded_images = expanded_slide.get("images", [])
                                # If counts don't match, restore original
                                if len(expanded_images) != len(original_images):
                                    expanded_slide["images"] = original_images
                                else:
                                    # Preserve original image structure (id, caption, marker, etc.)
                                    for img_idx, orig_img in enumerate(original_images):
                                        if img_idx < len(expanded_images):
                                            # Merge: keep original keys, update only if expanded has new valid data
                                            merged_img = orig_img.copy()
                                            expanded_img = expanded_images[img_idx]
                                            # Only update caption if expanded version has a better one
                                            if expanded_img.get("caption") and len(expanded_img.get("caption", "")) > len(orig_img.get("caption", "")):
                                                merged_img["caption"] = expanded_img["caption"]
                                            expanded_images[img_idx] = merged_img
                                    expanded_slide["images"] = expanded_images
                    
                    result["content"] = content
                    result["text"] = json.dumps(content, indent=2)  # Update text with preserved images
                    
                    # Preserve image markers if any were included
                    aggregated_markers = list(result.get("image_markers", []))
                    for slide in content.get("slides", []):
                        for image in slide.get("images", []):
                            aggregated_markers.append({
                                "marker": image.get("marker") or image.get("id"),
                                "description": image.get("caption") or image.get("alt_text") or image.get("marker") or image.get("id"),
                                "placement": image.get("placement", "auto"),
                                "slide_title": slide.get("title")
                            })
                    result["image_markers"] = aggregated_markers
            except Exception as e:
                logger.warning(f"Failed to parse expanded slide JSON: {e}")
                # On failure, return the original text so caller can fall back
        
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
        """Generate speaker notes for a slide based on ACTUAL slide content, not the topic"""
        content_text = "\n".join([f"- {point}" for point in slide_content])
        
        prompt = f"""CRITICAL: Generate detailed speaker notes based ONLY on the ACTUAL slide content provided below. 
DO NOT generate generic notes about the topic. Focus EXCLUSIVELY on the specific content in the bullets.

Slide Title: {slide_title}

ACTUAL Slide Content (bullets):
{content_text}

INSTRUCTIONS:
- Generate speaker notes that directly reference and elaborate on EACH bullet point shown above
- Do NOT create generic notes about "{slide_title}" as a topic
- Base your notes on the SPECIFIC content in the bullets provided
- For each bullet, create talking points that explain and expand on that specific point
- Provide examples that relate to the actual content in the bullets
- Create transitions that reference the actual content discussed

Generate:
- Main talking points (based on the actual bullets)
- Detailed talking points (elaborating each bullet)
- Examples to mention (related to the actual content)
- Transitions to next slide (referencing the actual content)
- Audience engagement questions (about the actual content)

Format as JSON:
{{
  "main_points": ["Point 1 based on actual content", "Point 2 based on actual content"],
  "talking_points": ["Detailed explanation of bullet 1", "Detailed explanation of bullet 2"],
  "examples": ["Example related to actual content", "Another example"],
  "transitions": ["Transition referencing actual content"],
  "engagement": ["Question about actual content", "Another question"]
}}"""
        
        result = self.generate(prompt, context, max_length=2048)  # Increased for detailed speaker notes
        
        if result["success"]:
            import json
            import re
            
            # Try to extract and parse JSON
            json_str = None
            json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
            if json_match:
                json_str = json_match.group()
            
            # First attempt: direct JSON parsing
            parsed = False
            if json_str:
                try:
                    content = json.loads(json_str)
                    result["notes"] = content
                    parsed = True
                except json.JSONDecodeError:
                    pass
            
            # Second attempt: clean and retry
            if not parsed and json_str:
                try:
                    # Remove control characters but preserve structure
                    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', ' ', json_str)
                    # Fix common JSON issues: missing commas, trailing commas
                    cleaned = re.sub(r',\s*}', '}', cleaned)
                    cleaned = re.sub(r',\s*]', ']', cleaned)
                    # Fix unquoted keys (if any)
                    cleaned = re.sub(r'(\w+):', r'"\1":', cleaned)
                    content = json.loads(cleaned)
                    result["notes"] = content
                    parsed = True
                except (json.JSONDecodeError, Exception):
                    pass
            
            # Fallback: manual extraction if JSON parsing fails
            if not parsed:
                try:
                    raw_text = result["text"]
                    
                    def extract_array(field_name):
                        # Look for field: [ ... ] pattern
                        pattern = rf'"{field_name}"\s*:\s*\[(.*?)\]'
                        matches = re.findall(pattern, raw_text, re.DOTALL)
                        if not matches:
                            return []
                        arr_content = matches[0]
                        # Extract quoted strings from array
                        strings = re.findall(r'"((?:[^"\\]|\\.)*)"', arr_content)
                        # Clean up escaped sequences
                        cleaned_strings = []
                        for s in strings:
                            s = s.replace('\\"', '"')
                            s = s.replace('\\n', ' ')
                            s = s.replace('\\t', ' ')
                            s = s.replace('\\r', ' ')
                            s = re.sub(r'[\x00-\x1F]', ' ', s)  # Remove any remaining control chars
                            cleaned_strings.append(s.strip())
                        return [s for s in cleaned_strings if s]
                    
                    result["notes"] = {
                        "main_points": extract_array("main_points"),
                        "talking_points": extract_array("talking_points"),
                        "examples": extract_array("examples"),
                        "transitions": extract_array("transitions"),
                        "engagement": extract_array("engagement")
                    }
                    logger.info("Used fallback parser for speaker notes")
                except Exception as fallback_error:
                    logger.warning(f"All parsing methods failed: {fallback_error}")
                    # Return empty structure so the code doesn't crash
                    result["notes"] = {
                        "main_points": [],
                        "talking_points": [],
                        "examples": [],
                        "transitions": [],
                        "engagement": []
                    }
        
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

