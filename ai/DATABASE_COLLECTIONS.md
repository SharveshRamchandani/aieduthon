# Database Collections and Structures

This document lists all MongoDB collections used in the AI folder and their document structures.

## Collections Overview

The AI system uses **13 MongoDB collections**:

1. **prompts** - User prompts for slide generation
2. **slides** - Generated slide decks
3. **media** - Images and media assets
4. **quizzes** - Generated quizzes
5. **diagrams** - Generated diagrams
6. **translations** - Translated slide content
7. **analytics** - Analytics events
8. **templates** - Presentation templates
9. **jobs** - Background job tracking
10. **ai_cache** - Cached AI generation results
11. **ai_sessions** - AI generation sessions
12. **ai_outputs** - AI output logging
13. **ai_feedback** - User feedback on AI outputs

---

## 1. `prompts` Collection

**Purpose**: Stores user prompts for slide generation

**Indexes**:
- `userId` (ascending) + `timestamp` (descending)
- `locale` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "userId": String,
  "prompt_text": String,
  "timestamp": DateTime,
  "locale": String,
  "context": Object (optional),
  "status": String (default: "processed")
}
```

**Example**:
```json
{
  "_id": ObjectId("..."),
  "userId": "user123",
  "prompt_text": "Create a presentation about photosynthesis",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "locale": "en",
  "context": {
    "grade_level": "college",
    "subject": "science"
  },
  "status": "processed"
}
```

---

## 2. `slides` Collection

**Purpose**: Stores generated slide decks with all content

**Indexes**:
- `promptId` (ascending)
- `title` (text search)
- `style` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "promptId": String,
  "title": String,
  "sections": Array<String>,
  "bullets": Array<Array<String>>,
  "examples": Array<Array<String>>,
  "key_points": Array<Array<String>>,
  "image_placeholders": Array<Array<String>>,
  "image_markers": Array<Object>,
  "template_path": String (optional),
  "generated_notes": Array<String>,
  "speaker_notes": Array<Object>,
  "style": String,
  "media_refs": Array<String>,
  "diagram_refs": Array<String>,
  "quiz_refs": Array<String>,
  "localized_versions": Array<String>,
  "categories": {
    "subject": String,
    "subject_tags": Array<String>,
    "style": String,
    "style_tags": Array<String>,
    "audience": String,
    "audience_tags": Array<String>,
    "complexity": String,
    "topics": Array<String>
  },
  "template_metadata": Object,
  "metadata": {
    "total_slides": Number,
    "estimated_duration": Number,
    "difficulty_level": String,
    "target_audience": String,
    "generated_at": DateTime,
    "user_id": String,
    "context": Object
  }
}
```

**Speaker Notes Structure** (within `speaker_notes` array):
```json
{
  "slide_index": Number,
  "slide_title": String,
  "notes": String,
  "key_points": Array<String>,
  "examples": Array<String>,
  "audience_engagement": String
}
```

---

## 3. `media` Collection

**Purpose**: Stores images and media assets (AI-generated, stock images, diagrams)

**Indexes**:
- `linked_slideId` (ascending)
- `type` (ascending)
- `locale` (ascending)
- `tags` (ascending)

**Document Structure** (AI-Generated Images):
```json
{
  "_id": ObjectId,
  "url": String,
  "alt_text": String,
  "source": String ("ai_generated" | "stock_image" | "internal"),
  "type": String ("image" | "diagram"),
  "linked_slideId": ObjectId (optional),
  "locale": String,
  "tags": Array<String>,
  "generated_by_ai": Boolean,
  "generation_prompt": String (optional),
  "created_at": DateTime,
  "session_id": ObjectId (optional),
  "metadata": {
    "model": String,
    "prompt": String,
    "width": Number,
    "height": Number
  }
}
```

**Document Structure** (Stock Images):
```json
{
  "_id": ObjectId,
  "type": "stock_image",
  "provider": String,
  "image_id": String,
  "url": String,
  "thumbnail": String (optional),
  "full_url": String (optional),
  "description": String,
  "author": String (optional),
  "author_url": String (optional),
  "slide_title": String (optional),
  "query": String,
  "marker": Object (optional),
  "width": Number (optional),
  "height": Number (optional),
  "created_at": DateTime
}
```

---

## 4. `quizzes` Collection

**Purpose**: Stores generated quizzes for slides

**Indexes**:
- `slideId` (ascending)
- `injected_position` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "slideId": String,
  "title": String,
  "questions": Array<{
    "question_text": String,
    "question_type": String,
    "options": Array<String>,
    "correct_answer": String,
    "explanation": String,
    "difficulty": String,
    "topic": String
  }>,
  "accuracy_stats": {
    "total_attempts": Number,
    "correct_attempts": Number,
    "average_score": Number
  },
  "live_quiz_export": Object (optional, for Google Forms),
  "injected_position": String ("after_section" | "final"),
  "metadata": {
    "total_questions": Number,
    "estimated_time": Number,
    "difficulty_level": String,
    "topics_covered": Array<String>,
    "generated_at": DateTime,
    "user_id": String
  }
}
```

---

## 5. `diagrams` Collection

**Purpose**: Stores generated diagrams (flowcharts, charts, cycles, etc.)

**Indexes**:
- `slideId` (ascending)
- `diagram_type` (ascending)
- `tags` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "slideId": ObjectId (optional),
  "diagram_type": String ("flowchart" | "chart" | "cycle" | "generic"),
  "description": String,
  "file_path": String,
  "format": String ("png" | "svg" | "pdf"),
  "tags": Array<String>,
  "created_at": DateTime
}
```

---

## 6. `translations` Collection

**Purpose**: Stores translated versions of slide content

**Indexes**:
- `slideId` (ascending) + `lang_code` (ascending) - **UNIQUE**
- `locale` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "slideId": ObjectId,
  "lang_code": String,
  "locale": String,
  "translated_content": Object,
  "created_at": DateTime
}
```

**Note**: The exact structure of `translated_content` may vary based on implementation.

---

## 7. `analytics` Collection

**Purpose**: Stores analytics events for tracking usage

**Indexes**:
- `userId` (ascending) + `timestamp` (descending)
- `deckId` (ascending)
- `template_used` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "userId": String,
  "timestamp": DateTime,
  "deckId": String,
  "event_type": String,
  "data": Object,
  "service": String,
  "template_used": String (optional)
}
```

**Example Event Types**:
- `slide_generated`
- `quiz_generated`
- `notes_generated`
- `media_integrated`

---

## 8. `templates` Collection

**Purpose**: Stores presentation templates

**Indexes**:
- `templateId` (ascending) - **UNIQUE**
- `recommended_for_audience` (ascending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "templateId": String,
  "name": String,
  "style": String,
  "recommended_for_audience": String,
  "popularity_stats": {
    "usage_count": Number,
    "rating": Number
  },
  "created_at": DateTime
}
```

**Example Templates**:
- `academic_modern` - style: "clean_minimal", audience: "college"
- `school_colorful` - style: "bright_engaging", audience: "school"
- `corporate_professional` - style: "business_formal", audience: "training"

---

## 9. `jobs` Collection

**Purpose**: Tracks background jobs and their status

**Indexes**:
- `jobId` (ascending) - **UNIQUE**
- `service_type` (ascending)
- `status` (ascending)
- `timestamp` (descending)

**Document Structure**:
```json
{
  "_id": ObjectId,
  "jobId": String,
  "service_type": String,
  "status": String ("pending" | "processing" | "completed" | "failed"),
  "timestamp": DateTime,
  "input": Object,
  "output": Object (optional),
  "error": String (optional),
  "metadata": Object (optional)
}
```

---

## 10. `ai_cache` Collection

**Purpose**: Caches AI generation results to avoid redundant API calls

**Document Structure**:
```json
{
  "_id": ObjectId,
  "cache_key": String,
  "result": String | Array | Object,
  "metadata": Object,
  "type": String (optional, e.g., "text" | "image" | "stock_image"),
  "ttl": Number (timestamp),
  "created_at": DateTime
}
```

**Usage**:
- Text generation results are cached with MD5 hash of prompt + context
- Image generation results are cached with prompt + dimensions
- TTL (Time To Live) is set as timestamp for expiration

---

## 11. `ai_sessions` Collection

**Purpose**: Tracks AI generation sessions for auditing and analytics

**Document Structure**:
```json
{
  "_id": ObjectId,
  "prompt": String,
  "context": Object,
  "model": String,
  "status": String ("processing" | "completed" | "failed"),
  "success": Boolean,
  "created_at": DateTime,
  "updated_at": DateTime,
  "metadata": Object (optional)
}
```

**Usage**:
- Created when generation starts
- Updated when generation completes or fails
- Links to outputs via `session_id` in `ai_outputs` collection

---

## 12. `ai_outputs` Collection

**Purpose**: Logs all AI generation outputs for auditing and analytics

**Document Structure** (Text Outputs):
```json
{
  "_id": ObjectId,
  "session_id": ObjectId (optional),
  "prompt": String,
  "generated_text": String,
  "metadata": Object,
  "model": String,
  "created_at": DateTime
}
```

**Document Structure** (Image Outputs):
```json
{
  "_id": ObjectId,
  "type": "image",
  "session_id": ObjectId (optional),
  "prompt": String,
  "file_path": String,
  "metadata": Object,
  "model": String,
  "created_at": DateTime
}
```

---

## 13. `ai_feedback` Collection

**Purpose**: Stores user feedback on AI-generated content for model improvement

**Document Structure**:
```json
{
  "_id": ObjectId,
  "prompt": String,
  "generated_text": String,
  "rating": Number (1-5),
  "feedback": String (optional),
  "user_id": String (optional),
  "model": String,
  "created_at": DateTime
}
```

---

## Database Connection

**Database Name**: Configured via `AI_MONGODB_URI` environment variable

**Connection File**: `ai/src/ai_db.py`

**Initialization**: Run `python init_db.py` to create all collections and indexes

---

## Relationships Between Collections

```
prompts (1) ──→ (many) slides
slides (1) ──→ (many) media (via media_refs)
slides (1) ──→ (many) quizzes (via quiz_refs)
slides (1) ──→ (many) diagrams (via diagram_refs)
slides (1) ──→ (many) translations
ai_sessions (1) ──→ (many) ai_outputs (via session_id)
```

---

## Notes

- All collections use MongoDB's default `_id` field as primary key
- Timestamps are stored as `DateTime` objects (ISO format)
- ObjectId references are used for relationships between collections
- Text search indexes are available on `slides.title` for full-text search
- Unique indexes prevent duplicate entries where needed (e.g., `templateId`, `jobId`)
- Collections are created automatically by `init_db.py` with proper indexes
