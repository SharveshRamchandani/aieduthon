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
	llm_provider: str = os.getenv("LLM_PROVIDER", "huggingface")
	hf_api_key: str = os.getenv("HF_API_KEY", "")
	hf_model_id: str = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
	gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
	gemini_model_id: str = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash")


def get_config() -> AIConfig:
	return AIConfig()
