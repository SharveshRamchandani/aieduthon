import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def connect_to_ai_mongo() -> Database:
	"""Connect to the AI MongoDB using AI_MONGODB_URI and AI_DB_NAME.

	Returns the Database object. Subsequent calls reuse the same client.
	"""
	global _client, _db

	if _db is not None:
		return _db

	# Load env from the ai/.env file (two levels up from this file: ai/src/ai_db.py -> ai/.env)
	ai_env_path = Path(__file__).resolve().parents[1] / ".env"
	load_dotenv(dotenv_path=ai_env_path, override=False)

	mongo_uri = os.getenv("AI_MONGODB_URI")
	db_name = os.getenv("AI_DB_NAME")
	if not mongo_uri:
		raise RuntimeError("AI_MONGODB_URI is not set in environment.")
	if not db_name:
		raise RuntimeError("AI_DB_NAME is not set in environment.")

	_client = MongoClient(mongo_uri)
	_db = _client[db_name]
	# Simple ping to verify connection
	_db.client.admin.command("ping")
	return _db


def get_ai_db() -> Database:
	"""Return the connected AI Database. Call connect_to_ai_mongo() first if needed."""
	if _db is None:
		return connect_to_ai_mongo()
	return _db


def close_ai_mongo() -> None:
	"""Close the AI MongoDB client if open."""
	global _client, _db
	if _client is not None:
		_client.close()
		_client = None
		_db = None
