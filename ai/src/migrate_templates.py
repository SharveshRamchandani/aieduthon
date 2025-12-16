"""
Quick script to migrate templates to MongoDB.
Run this after init_db.py to upload all PPTX templates to the database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.migrate_templates_to_db import migrate_templates_to_db

if __name__ == "__main__":
    print("=" * 60)
    print("Template Migration to MongoDB")
    print("=" * 60)
    migrate_templates_to_db()
    print("\n" + "=" * 60)
    print("Migration complete! Templates are now stored in MongoDB.")
    print("=" * 60)

