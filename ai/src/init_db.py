"""
Initialize AI database with all required collections, indexes, and sample data.
Run this once to set up the complete schema for the AI presentation system.
"""

from datetime import datetime
from ai_db import connect_to_ai_mongo, close_ai_mongo


def create_collections_and_indexes():
    """Create all collections with proper indexes for the AI system."""
    db = connect_to_ai_mongo()
    
    print("Creating collections and indexes...")
    
    # 1. Prompts collection
    prompts = db["prompts"]
    prompts.create_index([("userId", 1), ("timestamp", -1)])
    prompts.create_index([("locale", 1)])
    print("[OK] Created prompts collection with indexes")
    
    # 2. Slides collection
    slides = db["slides"]
    slides.create_index([("promptId", 1)])
    slides.create_index([("title", "text")])  # Text search
    slides.create_index([("style", 1)])
    print("[OK] Created slides collection with indexes")
    
    # 3. Media collection
    media = db["media"]
    media.create_index([("linked_slideId", 1)])
    media.create_index([("type", 1)])
    media.create_index([("locale", 1)])
    media.create_index([("tags", 1)])
    print("[OK] Created media collection with indexes")
    
    # 4. Quizzes collection
    quizzes = db["quizzes"]
    quizzes.create_index([("slideId", 1)])
    quizzes.create_index([("injected_position", 1)])
    print("[OK] Created quizzes collection with indexes")
    
    # 5. Diagrams collection
    diagrams = db["diagrams"]
    diagrams.create_index([("slideId", 1)])
    diagrams.create_index([("diagram_type", 1)])
    diagrams.create_index([("tags", 1)])
    print("[OK] Created diagrams collection with indexes")
    
    # 6. Translations collection
    translations = db["translations"]
    translations.create_index([("slideId", 1), ("lang_code", 1)], unique=True)
    translations.create_index([("locale", 1)])
    print("[OK] Created translations collection with indexes")
    
    # 7. Analytics collection
    analytics = db["analytics"]
    analytics.create_index([("userId", 1), ("timestamp", -1)])
    analytics.create_index([("deckId", 1)])
    analytics.create_index([("template_used", 1)])
    print("[OK] Created analytics collection with indexes")
    
    # 8. Templates collection
    templates = db["templates"]
    templates.create_index([("templateId", 1)], unique=True)
    templates.create_index([("recommended_for_audience", 1)])
    print("[OK] Created templates collection with indexes")
    
    # 9. Jobs collection
    jobs = db["jobs"]
    jobs.create_index([("jobId", 1)], unique=True)
    jobs.create_index([("service_type", 1)])
    jobs.create_index([("status", 1)])
    jobs.create_index([("timestamp", -1)])
    print("[OK] Created jobs collection with indexes")
    
    print("\nAll collections created successfully!")


def seed_sample_data():
    """Add sample templates and initial data."""
    db = connect_to_ai_mongo()
    
    print("\nSeeding sample data...")
    
    # Sample templates
    templates = db["templates"]
    sample_templates = [
        {
            "templateId": "academic_modern",
            "name": "Academic Modern",
            "style": "clean_minimal",
            "recommended_for_audience": "college",
            "popularity_stats": {"usage_count": 0, "rating": 4.5},
            "created_at": datetime.utcnow()
        },
        {
            "templateId": "school_colorful",
            "name": "School Colorful",
            "style": "bright_engaging",
            "recommended_for_audience": "school",
            "popularity_stats": {"usage_count": 0, "rating": 4.2},
            "created_at": datetime.utcnow()
        },
        {
            "templateId": "corporate_professional",
            "name": "Corporate Professional",
            "style": "business_formal",
            "recommended_for_audience": "training",
            "popularity_stats": {"usage_count": 0, "rating": 4.7},
            "created_at": datetime.utcnow()
        }
    ]
    
    for template in sample_templates:
        templates.update_one(
            {"templateId": template["templateId"]},
            {"$set": template},
            upsert=True
        )
    
    print("[OK] Seeded sample templates")
    
    # Sample media assets (placeholders)
    media = db["media"]
    sample_media = [
        {
            "url": "placeholder://academic-icon.png",
            "alt_text": "Academic icon",
            "source": "internal",
            "type": "image",
            "linked_slideId": None,
            "locale": "en",
            "tags": ["academic", "icon"],
            "generated_by_ai": False,
            "created_at": datetime.utcnow()
        },
        {
            "url": "placeholder://diagram-template.svg",
            "alt_text": "Process diagram template",
            "source": "internal",
            "type": "diagram",
            "linked_slideId": None,
            "locale": "en",
            "tags": ["diagram", "process"],
            "generated_by_ai": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    for asset in sample_media:
        media.insert_one(asset)
    
    print("[OK] Seeded sample media assets")
    
    print("\nSample data seeded successfully!")


def verify_setup():
    """Verify all collections exist and have proper structure."""
    db = connect_to_ai_mongo()
    
    print("\nVerifying database setup...")
    
    expected_collections = [
        "prompts", "slides", "media", "quizzes", 
        "diagrams", "translations", "analytics", 
        "templates", "jobs"
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection_name in expected_collections:
        if collection_name in existing_collections:
            count = db[collection_name].count_documents({})
            print(f"[OK] {collection_name}: {count} documents")
        else:
            print(f"[ERROR] {collection_name}: MISSING")
    
    print(f"\nDatabase setup complete! Connected to: {db.name}")


def main():
    """Main initialization function."""
    try:
        print("Initializing AI Database...")
        print("=" * 50)
        
        create_collections_and_indexes()
        seed_sample_data()
        verify_setup()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] AI Database initialization completed successfully!")
        print("You can now start building your AI presentation system.")
        
    except Exception as e:
        print(f"[ERROR] Error during initialization: {e}")
        raise
    finally:
        close_ai_mongo()


if __name__ == "__main__":
    main()
