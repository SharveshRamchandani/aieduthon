import os
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def connect_to_mongo() -> Database:
	"""Connect to MongoDB using MONGODB_URI and DB_NAME from environment.

	Returns the Database object. Subsequent calls reuse the same client.
	"""
	global _client, _db

	if _db is not None:
		return _db

	# Load .env once (safe to call multiple times)
	load_dotenv()

	mongo_uri = os.getenv("MONGODB_URI")
	db_name = os.getenv("DB_NAME")
	if not mongo_uri:
		raise RuntimeError("MONGODB_URI is not set in environment.")
	if not db_name:
		raise RuntimeError("DB_NAME is not set in environment.")

	_client = MongoClient(mongo_uri)
	_db = _client[db_name]
	# Simple ping to verify connection
	_db.client.admin.command("ping")
	return _db


def get_db() -> Database:
	"""Return the connected Database. Call connect_to_mongo() first if needed."""
	if _db is None:
		return connect_to_mongo()
	return _db


def close_mongo() -> None:
	"""Close the MongoDB client if open."""
	global _client, _db
	if _client is not None:
		_client.close()
		_client = None
		_db = None
