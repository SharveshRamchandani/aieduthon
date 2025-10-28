from datetime import datetime
from pprint import pprint

from ai_db import connect_to_ai_mongo, close_ai_mongo


def main() -> None:
	try:
		db = connect_to_ai_mongo()
		print(f"Connected to AI MongoDB database: {db.name}")

		# Demo write/read into AI-specific collection
		collection = db["ai_healthchecks"]
		result = collection.insert_one({
			"service": "ai-bootstrap",
			"ok": True,
			"timestamp": datetime.utcnow(),
		})
		print(f"Inserted document id: {result.inserted_id}")

		found = collection.find_one({"_id": result.inserted_id})
		print("Fetched back:")
		pprint(found)
	finally:
		close_ai_mongo()


if __name__ == "__main__":
	main()
