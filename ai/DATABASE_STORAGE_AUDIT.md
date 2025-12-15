# Database Storage Audit

This document outlines what data is being stored in the database for each slide deck.

## Overview

All slide deck data is stored in MongoDB in the `slides` collection. Additional data is stored in related collections (`media`, `quizzes`, `analytics`).

## Data Storage Status

### ✅ 1. Speaker Notes
**Status:** ✅ **STORED IN DB**

**Location:** `slides` collection, field: `speaker_notes`

**Storage Method:**
- Stored by `SpeakerNotesAgent._store_speaker_notes()` (line 318-340 in `speaker_notes_agent.py`)
- Updates the deck document with an array of speaker note objects
- Each note contains:
  - `slide_title`
  - `main_points`
  - `talking_points`
  - `examples`
  - `transitions`
  - `timing_notes`
  - `audience_engagement`

**Code Reference:**
```python
# ai/src/agents/speaker_notes_agent.py:337-339
self.slides_collection.update_one(
    {"_id": object_id},
    {"$set": {"speaker_notes": notes_data}}
)
```

---

### ✅ 2. PPT Files
**Status:** ✅ **STORED IN DB** (when `save_to_db=True`)

**Location:** `slides` collection, fields:
- `ppt_file` (base64 encoded string)
- `ppt_filename`
- `ppt_generated_at`
- `ppt_size_bytes`

**Storage Method:**
- Stored by `PPTExporter._save_ppt_to_db()` (line 258-281 in `ppt_exporter.py`)
- Called from `export_deck_to_bytes()` when `save_to_db=True` (line 52)
- PPT file is base64 encoded before storage
- **Note:** Only saved for PPTX format, not PDF

**Code Reference:**
```python
# ai/src/exporters/ppt_exporter.py:51-52
if save_to_db:
    self._save_ppt_to_db(deck_id, ppt_bytes, fname)

# ai/src/exporters/ppt_exporter.py:277-280
self.slides_collection.update_one(
    {"_id": object_id},
    {"$set": update_data}  # Contains ppt_file, ppt_filename, etc.
)
```

**Current Behavior:**
- In `export.py` route, `save_to_db=(body.format == "pptx")` - only saves PPTX, not PDF
- In `orchestrate.py`, `save_to_db` defaults to `True` but is not explicitly set

---

### ✅ 3. Stock Images
**Status:** ✅ **STORED IN DB** (in two places)

**Location 1:** `media` collection
- Full stock image metadata stored here
- Fields include: `type`, `provider`, `url`, `thumbnail`, `description`, `author`, etc.

**Location 2:** `slides` collection, fields:
- `media_refs` - Array of arrays, each sub-array contains URLs for that slide
- `diagram_refs` - Array of arrays for diagram file paths
- `media_metadata` - Detailed metadata for each media item
- `media_generated_at` - Timestamp

**Storage Method:**
1. **Individual images** stored in `media` collection by `StockImageAgent.get_image_for_slide()` (line 329 in `stock_image_agent.py`)
2. **Media references** stored in `slides` collection by `MediaIntegrationAgent.generate_media_for_deck()` (line 256-266 in `media_integration_agent.py`)

**Code Reference:**
```python
# ai/src/agents/stock_image_agent.py:329
media_result = self.media_collection.insert_one(media_doc)

# ai/src/agents/media_integration_agent.py:256-266
self.slides_collection.update_one(
    {"_id": ObjectId(deck_id)},
    {
        "$set": {
            "media_refs": media_refs,      # URLs array per slide
            "diagram_refs": diagram_refs,   # Diagram paths array per slide
            "media_metadata": media_metadata, # Detailed metadata
            "media_generated_at": datetime.utcnow()
        }
    }
)
```

---

### ✅ 4. Quiz References
**Status:** ✅ **STORED IN DB**

**Location 1:** `quizzes` collection
- Full quiz documents with questions, answers, metadata

**Location 2:** `slides` collection, field: `quiz_refs`
- Array of quiz IDs that reference this deck

**Storage Method:**
- Quizzes stored in `quizzes` collection by `QuizGenerationAgent._store_quiz()` (line 371 in `quiz_generation_agent.py`)
- Quiz references stored in `slides` collection by `QuizGenerationAgent._update_deck_quiz_refs()` (line 380-383 in `quiz_generation_agent.py`)

**Code Reference:**
```python
# ai/src/agents/quiz_generation_agent.py:380-383
self.slides_collection.update_one(
    {"_id": object_id},
    {"$set": {"quiz_refs": quiz_ids}}
)
```

---

## Complete Slide Deck Document Structure

A complete slide deck document in the `slides` collection should contain:

```javascript
{
  "_id": ObjectId("..."),
  "promptId": "...",
  "title": "...",
  "sections": [...],
  "bullets": [[...], [...]],
  "examples": [[...], [...]],
  "key_points": [[...], [...]],
  "image_placeholders": [[...], [...]],
  "image_markers": [...],
  "template_path": "...",
  "generated_notes": [...],
  
  // ✅ Speaker Notes (stored by SpeakerNotesAgent)
  "speaker_notes": [
    {
      "slide_title": "...",
      "main_points": [...],
      "talking_points": [...],
      "examples": [...],
      "transitions": [...],
      "timing_notes": [...],
      "audience_engagement": [...]
    }
  ],
  
  // ✅ PPT File (stored by PPTExporter when save_to_db=True)
  "ppt_file": "base64_encoded_string...",
  "ppt_filename": "...",
  "ppt_generated_at": ISODate("..."),
  "ppt_size_bytes": 12345,
  
  // ✅ Media References (stored by MediaIntegrationAgent)
  "media_refs": [
    ["url1", "url2"],  // URLs for slide 0
    ["url3"]            // URLs for slide 1
  ],
  "diagram_refs": [
    ["path1"],          // Diagram paths for slide 0
    []                  // No diagrams for slide 1
  ],
  "media_metadata": [
    [
      {
        "url": "...",
        "source": "stock",
        "provider": "unsplash",
        "media_id": "...",
        ...
      }
    ]
  ],
  "media_generated_at": ISODate("..."),
  
  // ✅ Quiz References (stored by QuizGenerationAgent)
  "quiz_refs": ["quiz_id_1", "quiz_id_2"],
  
  "style": "...",
  "localized_versions": [],
  "categories": [...],
  "created_at": ISODate("..."),
  ...
}
```

---

## Potential Issues & Recommendations

### 1. PPT File Storage
**Issue:** PPT files are only saved when `save_to_db=True`, which is:
- ✅ Set to `True` by default in `export_deck_to_bytes()`
- ✅ Only saves PPTX format, not PDF (by design)
- ⚠️ In `orchestrate.py`, the export doesn't explicitly set `save_to_db`, so it uses default `True`

**Recommendation:** Ensure `save_to_db=True` is always set when exporting in orchestrate flow.

### 2. Media Storage
**Status:** ✅ Working correctly
- Stock images are stored in `media` collection
- References are stored in `slides.media_refs`
- Metadata is stored in `slides.media_metadata`

### 3. Speaker Notes
**Status:** ✅ Working correctly
- Stored directly in `slides.speaker_notes` array

### 4. Quiz References
**Status:** ✅ Working correctly
- Quizzes stored in `quizzes` collection
- References stored in `slides.quiz_refs` array

---

## Verification Queries

To verify data is being stored, run these MongoDB queries:

```javascript
// Check if speaker notes exist
db.slides.findOne({_id: ObjectId("deck_id")}, {speaker_notes: 1})

// Check if PPT file exists
db.slides.findOne({_id: ObjectId("deck_id")}, {ppt_file: 1, ppt_filename: 1})

// Check if media references exist
db.slides.findOne({_id: ObjectId("deck_id")}, {media_refs: 1, media_metadata: 1})

// Check if quiz references exist
db.slides.findOne({_id: ObjectId("deck_id")}, {quiz_refs: 1})

// Check stock images in media collection
db.media.find({type: "stock_image", slide_title: "..."})

// Check quizzes
db.quizzes.find({slideId: "deck_id"})
```

