"""
Model Manager: Handles dynamic model loading, quantization, and caching
for plug-and-play multimodal AI pipeline.
"""

import yaml
import torch
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from diffusers import StableDiffusionPipeline
from transformers import BlipProcessor, BlipForConditionalGeneration
import logging

from ..config import get_config

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
                    "active_model": "meta-llama/Llama-2-7b-chat-hf",
                    "quantization": {"enabled": True, "load_in_8bit": True}
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
                return {**model, **text_config.get("quantization", {}), 
                       **text_config.get("generation", {})}
        
        return text_config
    
    def get_image_model_config(self) -> Dict[str, Any]:
        """Get active image model configuration"""
        image_config = self.model_registry["models"]["image"]
        active_model = image_config["active_model"]
        
        # Find model in available models
        for model in image_config.get("available_models", []):
            if model["name"] == active_model:
                return {**model, **image_config.get("generation", {})}
        
        return image_config
    
    def load_text_model(self, model_name: Optional[str] = None, force_reload: bool = False):
        """Load text generation model with quantization support"""
        config = self.get_text_model_config()
        model_name = model_name or config["name"]
        cache_key = f"text_{model_name}"
        
        if cache_key in self.loaded_models and not force_reload:
            logger.info(f"Using cached text model: {model_name}")
            return self.loaded_models[cache_key]
        
        logger.info(f"Loading text model: {model_name}")
        
        try:
            # Setup quantization if enabled
            quantization_config = None
            if config.get("quantization", {}).get("enabled", False):
                if config.get("quantization", {}).get("load_in_8bit", False):
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        llm_int8_threshold=6.0
                    )
                elif config.get("quantization", {}).get("load_in_4bit", False):
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
            
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
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            else:
                model_kwargs["device_map"] = device_map
                if device_map == "auto" or device_map.startswith("cuda"):
                    model_kwargs["torch_dtype"] = torch.float16
            
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
        
        try:
            device_map = self.model_registry["deployment"].get("device", "auto")
            if device_map == "auto":
                device_map = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load Stable Diffusion pipeline
            pipe = StableDiffusionPipeline.from_pretrained(
                model_name,
                cache_dir=str(self.cache_dir),
                torch_dtype=torch.float16 if device_map == "cuda" else torch.float32
            )
            
            pipe = pipe.to(device_map)
            
            # Store in cache
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

