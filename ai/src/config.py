import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Ensure we read ai/.env by default
AI_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=AI_ENV_PATH, override=False)


@dataclass(frozen=True)
class AIConfig:
	ai_mongo_uri: str = os.getenv("AI_MONGODB_URI", "mongodb://localhost:27017")
	ai_db_name: str = os.getenv("AI_DB_NAME", "ai_db")
	llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
	hf_api_key: str = os.getenv("HF_API_KEY", "")
	hf_model_id: str = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")
	gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
	gemini_model_id: str = os.getenv("GEMINI_MODEL_ID", "gemma-3-1b-it")
	stability_api_key: str = os.getenv("STABILITY_API_KEY", "")
	# Stock image API keys
	unsplash_api_key: str = os.getenv("UNSPLASH_API_KEY", "")
	pexels_api_key: str = os.getenv("PEXELS_API_KEY", "")
	pixabay_api_key: str = os.getenv("PIXABAY_API_KEY", "")
	stock_image_provider: str = os.getenv("STOCK_IMAGE_PROVIDER", "unsplash")
	# Image source preference: "stock" (default) or "generate"
	image_source: str = os.getenv("IMAGE_SOURCE", "stock")


def get_config() -> AIConfig:
	return AIConfig()
