"""
Migrate PPTX templates from file system to MongoDB.
Run this once to upload all templates to the database.
Uses GridFS for templates larger than 16MB (MongoDB document limit).
"""

import base64
import logging
from pathlib import Path
from datetime import datetime
from gridfs import GridFS

from ai_db import connect_to_ai_mongo, close_ai_mongo
from agents.template_selection_agent import TEMPLATE_DIR, TEMPLATE_LIBRARY

logger = logging.getLogger(__name__)

# MongoDB document size limit is 16MB
MAX_DOCUMENT_SIZE = 16 * 1024 * 1024  # 16MB in bytes


def migrate_templates_to_db():
    """Upload all PPTX templates from file system to MongoDB using GridFS for large files"""
    db = connect_to_ai_mongo()
    templates_collection = db["templates"]
    fs = GridFS(db, collection="templates_fs")  # GridFS for large template files
    
    template_dir = TEMPLATE_DIR
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        return
    
    template_files = sorted(template_dir.glob("*.pptx"))
    logger.info(f"Found {len(template_files)} template files to migrate")
    
    migrated_count = 0
    skipped_count = 0
    gridfs_count = 0
    
    for template_path in template_files:
        try:
            filename = template_path.name
            filename_lower = filename.lower()
            
            # Check if template already exists in DB
            existing = templates_collection.find_one({"filename": filename})
            if existing:
                logger.info(f"Template '{filename}' already exists in DB, skipping...")
                skipped_count += 1
                continue
            
            # Read template file
            with open(template_path, 'rb') as f:
                template_bytes = f.read()
            
            template_size = len(template_bytes)
            template_id = filename_lower.replace(".pptx", "").replace(" ", "_")
            
            # Get metadata from TEMPLATE_LIBRARY
            metadata = TEMPLATE_LIBRARY.get(filename_lower, {})
            
            # Convert sets to lists for MongoDB storage
            subjects_set = metadata.get("subjects", {"general"})
            styles_set = metadata.get("styles", {"general"})
            audiences_set = metadata.get("audiences", {"school", "college", "professional"})
            
            subjects_list = list(subjects_set) if isinstance(subjects_set, set) else list(subjects_set) if subjects_set else ["general"]
            styles_list = list(styles_set) if isinstance(styles_set, set) else list(styles_set) if styles_set else ["general"]
            audiences_list = list(audiences_set) if isinstance(audiences_set, set) else list(audiences_set) if audiences_set else ["school", "college", "professional"]
            
            # Get first element for single-value fields
            style = styles_list[0] if styles_list else "general"
            recommended_audience = audiences_list[0] if audiences_list else "general"
            
            # Check if file is too large for regular document (16MB limit)
            # Base64 encoding increases size by ~33%, so check if base64 would exceed limit
            base64_size_estimate = int(template_size * 1.34)  # Approximate base64 size
            
            if base64_size_estimate > MAX_DOCUMENT_SIZE:
                # Use GridFS for large files
                logger.info(f"Template '{filename}' is large ({template_size} bytes), using GridFS...")
                
                # Store file in GridFS
                gridfs_file_id = fs.put(
                    template_bytes,
                    filename=filename,
                    templateId=template_id,
                    content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
                # Create template document with GridFS reference
                template_doc = {
                    "templateId": template_id,
                    "filename": filename,
                    "filename_lower": filename_lower,
                    "template_file_id": str(gridfs_file_id),  # GridFS file ID
                    "storage_type": "gridfs",  # Indicates GridFS storage
                    "template_size_bytes": template_size,
                    "subjects": subjects_list,
                    "styles": styles_list,
                    "audiences": audiences_list,
                    "style": style,
                    "recommended_for_audience": recommended_audience,
                    "popularity_stats": {
                        "usage_count": 0,
                        "rating": 4.5
                    },
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "source": "file_system_migration"
                }
                gridfs_count += 1
            else:
                # Use base64 for smaller files (faster access)
                template_base64 = base64.b64encode(template_bytes).decode("utf-8")
                
                template_doc = {
                    "templateId": template_id,
                    "filename": filename,
                    "filename_lower": filename_lower,
                    "template_file": template_base64,  # Store as base64
                    "storage_type": "base64",  # Indicates base64 storage
                    "template_size_bytes": template_size,
                    "subjects": subjects_list,
                    "styles": styles_list,
                    "audiences": audiences_list,
                    "style": style,
                    "recommended_for_audience": recommended_audience,
                    "popularity_stats": {
                        "usage_count": 0,
                        "rating": 4.5
                    },
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "source": "file_system_migration"
                }
            
            # Insert into database
            templates_collection.insert_one(template_doc)
            logger.info(f"✓ Migrated template: {filename} ({template_size} bytes, storage: {template_doc.get('storage_type', 'base64')})")
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"✗ Failed to migrate template {template_path.name}: {e}")
    
    logger.info(f"\nMigration complete!")
    logger.info(f"  Migrated: {migrated_count} templates")
    logger.info(f"  Using GridFS: {gridfs_count} templates")
    logger.info(f"  Using base64: {migrated_count - gridfs_count} templates")
    logger.info(f"  Skipped (already exists): {skipped_count} templates")
    logger.info(f"  Total templates in DB: {templates_collection.count_documents({})}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        migrate_templates_to_db()
    finally:
        close_ai_mongo()

