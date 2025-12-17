# Data Storage Locations - Quick Reference

## 📍 Where Each Data Type is Saved

### 1. **Speaker Notes**
```
Collection: slides
Field: speaker_notes
Type: Array of objects
Code: ai/src/agents/speaker_notes_agent.py:337-339
```

**Example:**
```javascript
db.slides.findOne({_id: ObjectId("...")}, {speaker_notes: 1})
// Returns: { speaker_notes: [{ slide_title: "...", main_points: [...], ... }] }
```

---

### 2. **PPT Files**
```
Collection: slides
Fields: 
  - ppt_file (base64 string)
  - ppt_filename
  - ppt_generated_at
  - ppt_size_bytes
Code: ai/src/exporters/ppt_exporter.py:258-281
```

**Example:**
```javascript
db.slides.findOne({_id: ObjectId("...")}, {ppt_file: 1, ppt_filename: 1})
// Returns: { ppt_file: "base64_string...", ppt_filename: "Topic_user_2024-12-09.pptx" }
```

---

### 3. **Stock Images** (stored in 2 places)

#### A. Individual Image Records
```
Collection: media
Fields: type, provider, url, thumbnail, description, author, etc.
Code: ai/src/agents/stock_image_agent.py:329
```

**Example:**
```javascript
db.media.find({type: "stock_image"})
// Returns: [{ _id: ObjectId("..."), type: "stock_image", url: "...", provider: "unsplash", ... }]
```

#### B. Media References in Slide Deck
```
Collection: slides
Fields:
  - media_refs (array of URL arrays per slide)
  - diagram_refs (array of path arrays per slide)
  - media_metadata (detailed metadata per media item)
  - media_generated_at
Code: ai/src/agents/media_integration_agent.py:256-266
```

**Example:**
```javascript
db.slides.findOne({_id: ObjectId("...")}, {media_refs: 1, media_metadata: 1})
// Returns: { 
//   media_refs: [["url1", "url2"], ["url3"]],
//   media_metadata: [[{url: "...", source: "stock", ...}], [...]]
// }
```

---

### 4. **Quizzes** (stored in 2 places)

#### A. Full Quiz Documents
```
Collection: quizzes
Fields: questions, answers, metadata, etc.
Code: ai/src/agents/quiz_generation_agent.py:371
```

**Example:**
```javascript
db.quizzes.find({slideId: "deck_id"})
// Returns: [{ _id: ObjectId("..."), questions: [...], answers: [...], ... }]
```

#### B. Quiz References in Slide Deck
```
Collection: slides
Field: quiz_refs (array of quiz IDs)
Code: ai/src/agents/quiz_generation_agent.py:380-383
```

**Example:**
```javascript
db.slides.findOne({_id: ObjectId("...")}, {quiz_refs: 1})
// Returns: { quiz_refs: ["quiz_id_1", "quiz_id_2"] }
```

---

## 📊 Summary Table

| Data Type | Primary Collection | Field(s) | Secondary Collection | Secondary Field |
|-----------|-------------------|----------|---------------------|----------------|
| **Speaker Notes** | `slides` | `speaker_notes` | - | - |
| **PPT Files** | `slides` | `ppt_file`, `ppt_filename`, `ppt_generated_at`, `ppt_size_bytes` | - | - |
| **Stock Images** | `media` | Full document with `type: "stock_image"` | `slides` | `media_refs`, `media_metadata` |
| **Diagrams** | - | - | `slides` | `diagram_refs` |
| **Quizzes** | `quizzes` | Full quiz document | `slides` | `quiz_refs` |

---

## 🔍 Quick Verification Queries

```javascript
// 1. Check speaker notes
db.slides.findOne({_id: ObjectId("YOUR_DECK_ID")}, {speaker_notes: 1})

// 2. Check PPT file
db.slides.findOne({_id: ObjectId("YOUR_DECK_ID")}, {ppt_file: 1, ppt_filename: 1, ppt_generated_at: 1})

// 3. Check media references
db.slides.findOne({_id: ObjectId("YOUR_DECK_ID")}, {media_refs: 1, media_metadata: 1, media_generated_at: 1})

// 4. Check stock images in media collection
db.media.find({type: "stock_image"})

// 5. Check quiz references
db.slides.findOne({_id: ObjectId("YOUR_DECK_ID")}, {quiz_refs: 1})

// 6. Check full quiz documents
db.quizzes.find({slideId: "YOUR_DECK_ID"})
```

---

## 📝 Notes

- **All slide deck data** is stored in the `slides` collection
- **Stock images** are stored in both `media` collection (full records) and `slides.media_refs` (references)
- **Quizzes** are stored in both `quizzes` collection (full documents) and `slides.quiz_refs` (references)
- **PPT files** are base64-encoded strings stored directly in the `slides` collection
- **Speaker notes** are stored directly in the `slides` collection as an array

