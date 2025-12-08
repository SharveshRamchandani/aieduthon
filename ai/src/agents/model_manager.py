"""
Model Manager: Handles dynamic model loading, quantization, and caching
for plug-and-play multimodal AI pipeline.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Lazy imports for AI models - only load when needed
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM,
        BitsAndBytesConfig
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    AutoTokenizer = None
    AutoModelForCausalLM = None
    BitsAndBytesConfig = None

try:
    from diffusers import StableDiffusionPipeline
    try:
        from diffusers import StableDiffusion3Pipeline
    except ImportError:
        StableDiffusion3Pipeline = None
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False
    StableDiffusionPipeline = None
    StableDiffusion3Pipeline = None

import requests

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    HAS_VISION = True
except ImportError:
    HAS_VISION = False
    BlipProcessor = None
    BlipForConditionalGeneration = None

# Import config module (file) - use importlib to avoid directory conflict
import importlib.util
from pathlib import Path
config_file = Path(__file__).parent.parent / "config.py"
spec = importlib.util.spec_from_file_location("ai_config", config_file)
ai_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_config)
get_config = ai_config.get_config

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading, quantization, and caching for multimodal pipeline"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = get_config()
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "model_registry.yaml"
        self.model_registry = self._load_registry()
        self.loaded_models: Dict[str, Any] = {}
        self.cache_dir = Path(self.model_registry["deployment"]["cache_dir"])
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load model registry from YAML config"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Model registry not found at {self.config_path}, using defaults")
            return self._get_default_registry()
    
    def _get_default_registry(self) -> Dict[str, Any]:
        """Default model registry if YAML not found"""
        return {
            "models": {
                "text": {
                    "active_model": "mistralai/Mistral-7B-Instruct-v0.2",
                    "quantization": {"enabled": False, "load_in_8bit": False}
                },
                "image": {
                    "active_model": "stabilityai/stable-diffusion-2-1"
                }
            },
            "deployment": {
                "device": "auto",
                "cache_dir": "./models_cache"
            }
        }
    
    def get_text_model_config(self) -> Dict[str, Any]:
        """Get active text model configuration"""
        text_config = self.model_registry["models"]["text"]
        active_model = text_config["active_model"]
        
        # Find model in available models
        for model in text_config.get("available_models", []):
            if model["name"] == active_model:
                # Merge configs, but normalize quantization field
                merged_config = {**model}
                
                # Handle quantization: normalize boolean to dict if needed
                model_quantization = model.get("quantization")
                text_quantization = text_config.get("quantization", {})
                
                if isinstance(model_quantization, bool):
                    # If model has boolean quantization, use text_config quantization dict
                    # but enable it if the boolean is True
                    if model_quantization and isinstance(text_quantization, dict):
                        merged_config["quantization"] = text_quantization
                    else:
                        merged_config["quantization"] = {"enabled": model_quantization}
                elif isinstance(model_quantization, dict):
                    # Merge quantization dicts, model takes precedence
                    merged_config["quantization"] = {**text_quantization, **model_quantization}
                elif isinstance(text_quantization, dict):
                    merged_config["quantization"] = text_quantization
                else:
                    merged_config["quantization"] = {}
                
                # Merge generation settings
                merged_config.update(text_config.get("generation", {}))
                
                # Add provider, use_api, and api_version from text_config if not in model
                if "provider" not in merged_config:
                    merged_config["provider"] = text_config.get("provider")
                if "use_api" not in merged_config:
                    merged_config["use_api"] = text_config.get("use_api", False)
                if "api_version" not in merged_config:
                    # Get api_version from model config, or default based on model name
                    model_api_version = model.get("api_version")
                    if model_api_version:
                        merged_config["api_version"] = model_api_version
                    else:
                        # Default: v1beta for gemma models, v1 for others
                        if "gemma" in merged_config.get("name", "").lower():
                            merged_config["api_version"] = "v1beta"
                        else:
                            merged_config["api_version"] = "v1"
                
                return merged_config
        
        # If model not found in available_models, return text_config with defaults
        result = text_config.copy()
        if "provider" not in result:
            result["provider"] = None
        if "use_api" not in result:
            result["use_api"] = False
        return result
    
    def get_image_model_config(self) -> Dict[str, Any]:
        """Get active image model configuration"""
        image_config = self.model_registry["models"]["image"]
        active_model = image_config["active_model"]
        
        # Find model in available models
        for model in image_config.get("available_models", []):
            if model["name"] == active_model:
                merged = {**image_config.get("generation", {}), **model}
                return merged
        
        return image_config
    
    def load_text_model(self, model_name: Optional[str] = None, force_reload: bool = False):
        """Load text generation model with quantization support"""
        if not HAS_TRANSFORMERS or not HAS_TORCH:
            raise ImportError(
                "Transformers and PyTorch are required for text generation. "
                "Install with: pip install transformers torch"
            )
        
        config = self.get_text_model_config()
        model_name = model_name or config.get("name") or config.get("active_model")
        cache_key = f"text_{model_name}"
        
        if cache_key in self.loaded_models and not force_reload:
            logger.info(f"Using cached text model: {model_name}")
            return self.loaded_models[cache_key]
        
        logger.info(f"Loading text model: {model_name}")
        
        try:
            # Setup quantization if enabled and CUDA is available
            quantization_config = None
            quantization = config.get("quantization", {})
            # Ensure quantization is a dict (handle boolean case)
            if isinstance(quantization, bool):
                quantization = {"enabled": quantization}
            elif not isinstance(quantization, dict):
                quantization = {}
            
            # Check if CUDA is available for quantization
            cuda_available = HAS_TORCH and torch.cuda.is_available()
            
            if quantization.get("enabled", False) and cuda_available:
                try:
                    if quantization.get("load_in_8bit", False):
                        quantization_config = BitsAndBytesConfig(
                            load_in_8bit=True,
                            llm_int8_threshold=6.0
                        )
                    elif quantization.get("load_in_4bit", False):
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_use_double_quant=True,
                            bnb_4bit_quant_type="nf4"
                        )
                except Exception as e:
                    logger.warning(f"Failed to setup quantization (bitsandbytes may require CUDA): {e}. Falling back to non-quantized model.")
                    quantization_config = None
            elif quantization.get("enabled", False) and not cuda_available:
                logger.warning("Quantization requested but CUDA not available. Loading model without quantization.")
                quantization_config = None
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(self.cache_dir),
                trust_remote_code=True
            )
            
            # Set pad token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model
            device_map = self.model_registry["deployment"].get("device", "auto")
            model_kwargs = {
                "cache_dir": str(self.cache_dir),
                "trust_remote_code": True
            }
            
            # Auto-detect device if needed
            if device_map == "auto":
                device_map = "cuda" if cuda_available else "cpu"
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            else:
                model_kwargs["device_map"] = device_map
                # Only use float16 if CUDA is available, otherwise use float32 for CPU
                if device_map.startswith("cuda") and cuda_available:
                    model_kwargs["torch_dtype"] = torch.float16
                elif device_map == "cpu":
                    model_kwargs["torch_dtype"] = torch.float32
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **model_kwargs
            )
            
            # Store in cache
            self.loaded_models[cache_key] = {
                "model": model,
                "tokenizer": tokenizer,
                "config": config
            }
            
            logger.info(f"Successfully loaded text model: {model_name}")
            return self.loaded_models[cache_key]
            
        except Exception as e:
            logger.error(f"Error loading text model {model_name}: {e}")
            raise
    
    def load_image_model(self, model_name: Optional[str] = None, force_reload: bool = False):
        """Load image generation model"""
        config = self.get_image_model_config()
        model_name = model_name or config["name"]
        cache_key = f"image_{model_name}"
        
        if cache_key in self.loaded_models and not force_reload:
            logger.info(f"Using cached image model: {model_name}")
            return self.loaded_models[cache_key]
        
        logger.info(f"Loading image model: {model_name}")
        
        provider = config.get("provider")
        if provider == "huggingface":
            # No local pipeline to load; we store API metadata
            api_config = {
                "type": "huggingface",
                "endpoint": config.get("api_model", model_name)
            }
            self.loaded_models[cache_key] = {
                "pipe": None,
                "config": {**config, **api_config}
            }
            logger.info(f"Configured Hugging Face inference model: {model_name}")
            return self.loaded_models[cache_key]
        if provider == "stability":
            stability_config = {
                "type": "stability",
                "model_id": config.get("model_id", "stable-diffusion-xl-1024-v1-0"),
            }
            self.loaded_models[cache_key] = {
                "pipe": None,
                "config": {**config, **stability_config}
            }
            logger.info(f"Configured Stability AI hosted model: {model_name}")
            return self.loaded_models[cache_key]
        
        if not HAS_DIFFUSERS or not HAS_TORCH:
            raise ImportError(
                "Diffusers and PyTorch are required for local image generation. "
                "Install with: pip install diffusers torch"
            )
        
        try:
            device_map = self.model_registry["deployment"].get("device", "auto")
            if device_map == "auto":
                device_map = "cuda" if torch.cuda.is_available() else "cpu"
            
            model_source = config.get("weights_path") or model_name
            pipeline_type = config.get("pipeline", "sd15")
            torch_dtype = torch.float16 if device_map == "cuda" else torch.float32
            
            if pipeline_type == "sd3":
                if StableDiffusion3Pipeline is None:
                    raise ImportError(
                        "StableDiffusion3Pipeline not available. Upgrade diffusers to >=0.29.0"
                    )
                if device_map == "cuda" and hasattr(torch, "bfloat16"):
                    torch_dtype = torch.bfloat16
                pipe = StableDiffusion3Pipeline.from_pretrained(
                    model_source,
                    cache_dir=str(self.cache_dir),
                    torch_dtype=torch_dtype,
                    use_safetensors=True
                )
            else:
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_source,
                    cache_dir=str(self.cache_dir),
                    torch_dtype=torch_dtype,
                    use_safetensors=True
                )
            
            pipe = pipe.to(device_map)
            
            self.loaded_models[cache_key] = {
                "pipe": pipe,
                "config": config
            }
            
            logger.info(f"Successfully loaded image model: {model_name}")
            return self.loaded_models[cache_key]
            
        except Exception as e:
            logger.error(f"Error loading image model {model_name}: {e}")
            raise
    
    def load_vision_model(self, model_name: Optional[str] = None, force_reload: bool = False):
        """Load vision model for captioning/understanding"""
        if not HAS_VISION or not HAS_TORCH:
            raise ImportError(
                "Transformers and PyTorch are required for vision models. "
                "Install with: pip install transformers torch"
            )
        
        vision_config = self.model_registry["models"].get("vision", {})
        model_name = model_name or vision_config.get("active_model", "Salesforce/blip-image-captioning-base")
        cache_key = f"vision_{model_name}"
        
        if cache_key in self.loaded_models and not force_reload:
            logger.info(f"Using cached vision model: {model_name}")
            return self.loaded_models[cache_key]
        
        logger.info(f"Loading vision model: {model_name}")
        
        try:
            processor = BlipProcessor.from_pretrained(
                model_name,
                cache_dir=str(self.cache_dir)
            )
            model = BlipForConditionalGeneration.from_pretrained(
                model_name,
                cache_dir=str(self.cache_dir)
            )
            
            device_map = self.model_registry["deployment"].get("device", "auto")
            if device_map == "auto":
                device_map = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device_map)
            
            self.loaded_models[cache_key] = {
                "processor": processor,
                "model": model,
                "config": vision_config
            }
            
            logger.info(f"Successfully loaded vision model: {model_name}")
            return self.loaded_models[cache_key]
            
        except Exception as e:
            logger.error(f"Error loading vision model {model_name}: {e}")
            raise
    
    def unload_model(self, model_type: str, model_name: Optional[str] = None):
        """Unload a model from memory"""
        if model_name:
            cache_key = f"{model_type}_{model_name}"
        else:
            config = self.get_text_model_config() if model_type == "text" else self.get_image_model_config()
            cache_key = f"{model_type}_{config.get('name', 'unknown')}"
        
        if cache_key in self.loaded_models:
            del self.loaded_models[cache_key]
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logger.info(f"Unloaded model: {cache_key}")
    
    def get_available_models(self, model_type: str) -> list:
        """Get list of available models for a given type"""
        return self.model_registry["models"].get(model_type, {}).get("available_models", [])
    
    def switch_model(self, model_type: str, model_name: str):
        """Switch active model (updates config, requires reload)"""
        if model_type not in self.model_registry["models"]:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Verify model exists in available models
        available = [m["name"] for m in self.get_available_models(model_type)]
        if model_name not in available:
            raise ValueError(f"Model {model_name} not in available models: {available}")
        
        # Update active model
        self.model_registry["models"][model_type]["active_model"] = model_name
        
        # Unload old model
        self.unload_model(model_type)
        
        logger.info(f"Switched {model_type} model to: {model_name}")


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

