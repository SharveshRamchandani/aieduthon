# Template Storage in MongoDB

## Overview

PPTX templates are now stored in MongoDB instead of the file system. This allows:
- ✅ Templates accessible from anywhere (no file system dependencies)
- ✅ Easy template management and updates
- ✅ Better Docker compatibility
- ✅ Template versioning and metadata tracking

## Migration Steps

### 1. Initialize Database (if not done)
```bash
cd ai/src
python init_db.py
```

### 2. Migrate Templates to MongoDB
```bash
cd ai/src
python migrate_templates.py
```

This will:
- Read all `.pptx` files from `ppt dataset/` folder
- Upload them to MongoDB `templates` collection as base64
- Store metadata (subjects, styles, audiences)
- Skip templates that already exist

## How It Works

### Storage Structure

Templates are stored in MongoDB `templates` collection with:
```json
{
  "templateId": "black_and_grey_monocrome_business_company_presentation",
  "filename": "Black and Grey Monocrome Business Company Presentation.pptx",
  "filename_lower": "black and grey monocrome business company presentation.pptx",
  "template_file": "<base64_encoded_pptx_bytes>",
  "template_size_bytes": 123456,
  "subjects": ["business", "economics"],
  "styles": ["business_pitch", "general"],
  "audiences": ["professional", "training"],
  "popularity_stats": {"usage_count": 0, "rating": 4.5},
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Template Selection

- `TemplateSelectionAgent` now loads templates from MongoDB by default
- Returns template path as `"db:template_id"` instead of file path
- Falls back to file system if `use_db=False`

### Template Loading

- `PPTExporter` detects `"db:"` prefix in template_path
- Loads template from MongoDB and decodes base64
- Falls back to file system if template not found in DB

## Usage

### Automatic (Default)
Templates are automatically loaded from MongoDB. No code changes needed!

### Manual Template Upload
```python
from utils.migrate_templates_to_db import migrate_templates_to_db
migrate_templates_to_db()
```

### Check Templates in DB
```python
from ai_db import get_ai_db
db = get_ai_db()
templates = db["templates"]
count = templates.count_documents({})
print(f"Total templates in DB: {count}")
```

## Docker Compatibility

Templates are now stored in MongoDB, so:
- ✅ No need to copy `ppt dataset/` folder in Docker
- ✅ Templates work across all environments
- ✅ Easy to add/update templates via MongoDB

## Adding New Templates

1. Add `.pptx` file to `ppt dataset/` folder
2. Run migration: `python migrate_templates.py`
3. Template will be automatically available

## Fallback Behavior

If MongoDB template is not found:
- Falls back to file system `ppt dataset/` folder
- Logs warning but continues with default template

## Benefits

- **Portability**: Templates travel with database
- **Scalability**: Easy to manage thousands of templates
- **Versioning**: Can track template changes over time
- **Metadata**: Rich metadata for better template selection
- **Docker**: No file system dependencies

