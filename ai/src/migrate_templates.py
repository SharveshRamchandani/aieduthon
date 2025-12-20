"""
Quick script to migrate templates to MongoDB.
Run this after init_db.py to upload all PPTX templates to the database.

This variant first clears any existing templates in Mongo (both the
`templates` collection and the associated GridFS buckets) so that your
fresh, cleaned PPTX templates replace the old ones 1:1.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.migrate_templates_to_db import migrate_templates_to_db
from ai_db import connect_to_ai_mongo, close_ai_mongo


if __name__ == "__main__":
    print("=" * 60)
    print("Template Migration to MongoDB (reset + upload)")
    print("=" * 60)

    db = connect_to_ai_mongo()

    # Drop existing templates + GridFS buckets so we only have cleaned ones
    print("Dropping existing template collections in MongoDB...")
    db.drop_collection("templates")
    db.drop_collection("templates_fs.files")
    db.drop_collection("templates_fs.chunks")
    print("Existing templates removed.\n")

    try:
        migrate_templates_to_db()
    finally:
        close_ai_mongo()

    print("\n" + "=" * 60)
    print("Migration complete! Cleaned templates are now stored in MongoDB.")
    print("=" * 60)
