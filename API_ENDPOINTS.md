# API Endpoints for Postman

**Base URL:** `http://localhost:8000`

---

## 📋 Endpoint Order & Usage Flow

### **Recommended Flow:**
1. **POST /orchestrate** - Generate complete presentation (slides + notes + quizzes + media + PPT)
2. **GET /slides/{deck_id}** - Retrieve deck details
3. **POST /slides/{deck_id}/export** - Export as PPTX or PDF
4. **POST /slides/{deck_id}/quizzes?download=pdf** - Generate quiz and download as PDF
5. **POST /slides/{deck_id}/speaker-notes** - Generate speaker notes PDF

---

## 🎯 Main Endpoints

### 1. **POST /orchestrate** ⭐ (All-in-One)
**Description:** Generate complete presentation with slides, notes, quizzes, media, and PPT file.

**Request Body (JSON):**
```json
{
  "prompt": "Create a presentation about Photosynthesis",
  "userId": "user123",
  "locale": "en",
  "context": {
    "grade_level": "10th",
    "subject": "biology"
  },
  "quiz_type": "comprehensive",
  "quiz_questions": 5,
  "audience_level": "intermediate",
  "presentation_style": "educational",
  "generate_images": true,
  "generate_diagrams": true,
  "estimated_slides": 10
}
```

**Response:**
```json
{
  "deckId": "6937a4c2c5299b45ebf91e79",
  "promptId": "...",
  "quizIds": ["..."],
  "mediaGenerated": true,
  "pptFile": "base64...",
  "pptFilename": "presentation.pptx",
  "pptValidation": {...}
}
```

---

### 2. **POST /slides**
**Description:** Create slides only (without notes/quizzes).

**Request Body (JSON):**
```json
{
  "prompt": "Create a presentation about Machine Learning",
  "userId": "user123",
  "locale": "en",
  "context": {
    "grade_level": "college"
  }
}
```

**Response:**
```json
{
  "deckId": "6937a4c2c5299b45ebf91e79",
  "promptId": "..."
}
```

---

### 3. **GET /slides/{deck_id}**
**Description:** Get deck details by ID.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Example:** `GET /slides/6937a4c2c5299b45ebf91e79`

**Response:** Full deck object with slides, notes, media, etc.

---

### 4. **POST /slides/{deck_id}/export**
**Description:** Export deck as PPTX or PDF file.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Request Body (JSON):**
```json
{
  "output_dir": null,
  "format": "pptx",
  "user_name": "user"
}
```

**Options:**
- `format`: `"pptx"` or `"pdf"`
- `output_dir`: Optional (can be null)
- `user_name`: Used in filename

**Response:** Binary file download (PPTX or PDF)

**Example:** `POST /slides/6937a4c2c5299b45ebf91e79/export`

---

### 5. **GET /slides/{deck_id}/download**
**Description:** Download an already exported deck file.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Example:** `GET /slides/6937a4c2c5299b45ebf91e79/download`

**Response:** Binary file download (PPTX)

---

## 📝 Speaker Notes Endpoints

### 6. **POST /slides/{deck_id}/speaker-notes**
**Description:** Generate speaker notes for a deck and download as PDF.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Request Body (JSON):**
```json
{
  "userId": "user123",
  "audience_level": "intermediate",
  "presentation_style": "educational"
}
```

**Response:** Binary PDF file download

**Example:** `POST /slides/6937a4c2c5299b45ebf91e79/speaker-notes`

---

### 7. **GET /slides/{deck_id}/speaker-notes/download**
**Description:** Download previously generated speaker notes PDF.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck
- `file` (query) - Filename of the PDF

**Example:** `GET /slides/6937a4c2c5299b45ebf91e79/speaker-notes/download?file=speaker_notes_...pdf`

---

## 🎯 Quiz Endpoints

### 8. **POST /slides/{deck_id}/quizzes**
**Description:** Generate quiz for a deck. Can return JSON or PDF.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Query Parameters:**
- `download` (optional) - Set to `"pdf"` to download PDF instead of JSON

**Request Body (JSON):**
```json
{
  "userId": "user123",
  "quiz_type": "comprehensive",
  "difficulty": null
}
```

**Response (JSON):**
```json
{
  "success": true,
  "quiz_ids": ["..."],
  "quizType": "comprehensive"
}
```

**Response (PDF):** Binary PDF file download (when `?download=pdf`)

**Examples:**
- `POST /slides/6937a4c2c5299b45ebf91e79/quizzes` - Returns JSON
- `POST /slides/6937a4c2c5299b45ebf91e79/quizzes?download=pdf` - Downloads PDF

---

## 🎨 Generation Endpoints (Individual Components)

### 9. **POST /generate-text**
**Description:** Generate text using LLM only.

**Request Body (JSON):**
```json
{
  "prompt": "Explain photosynthesis",
  "context": {
    "grade_level": "10th"
  },
  "max_length": 2048,
  "temperature": 0.7,
  "use_cache": true
}
```

**Response:**
```json
{
  "success": true,
  "text": "...",
  "cached": false,
  "model": "gemini-flash-lite-latest"
}
```

---

### 10. **POST /generate-image**
**Description:** Generate image using AI.

**Request Body (JSON):**
```json
{
  "prompt": "Educational illustration of photosynthesis",
  "width": 1024,
  "height": 1024,
  "negative_prompt": "blurry, low quality",
  "num_images": 1,
  "use_cache": true
}
```

**Response:**
```json
{
  "success": true,
  "urls": ["..."],
  "cached": false,
  "model": "...",
  "mediaIds": ["..."],
  "captions": ["..."],
  "prompt": "...",
  "generatedAt": "..."
}
```

---

### 11. **POST /generate-diagram**
**Description:** Generate diagram (flowchart, cycle, etc.).

**Request Body (JSON):**
```json
{
  "diagram_type": "flowchart",
  "description": "Photosynthesis cycle showing conversion of sunlight to glucose",
  "data": null,
  "format": "png",
  "style": "educational"
}
```

**Response:**
```json
{
  "success": true,
  "file_path": "...",
  "diagram_id": "...",
  "type": "flowchart"
}
```

---

### 12. **POST /generate-slides**
**Description:** Generate slides with media (alternative to /orchestrate).

**Request Body (JSON):**
```json
{
  "prompt": "Create a presentation about AI",
  "userId": "user123",
  "locale": "en",
  "context": {},
  "generate_images": true,
  "generate_diagrams": true
}
```

**Response:**
```json
{
  "success": true,
  "deckId": "...",
  "promptId": "...",
  "metadata": {...}
}
```

---

### 13. **POST /generate-media/{deck_id}**
**Description:** Generate media (images/diagrams) for an existing deck.

**URL Parameters:**
- `deck_id` (path) - MongoDB ObjectId of the deck

**Query Parameters:**
- `generate_images` (default: `true`) - Boolean
- `generate_diagrams` (default: `true`) - Boolean

**Example:** `POST /generate-media/6937a4c2c5299b45ebf91e79?generate_images=true&generate_diagrams=true`

**Response:**
```json
{
  "success": true,
  "media_refs": ["..."],
  "diagram_refs": ["..."],
  "media_metadata": [...]
}
```

---

### 14. **POST /generate-notes**
**Description:** Generate lesson notes directly from prompt (standalone, not tied to a deck).

**Request Body (JSON):**
```json
{
  "prompt": "Create lesson notes about Photosynthesis",
  "userId": "user123",
  "audienceLevel": "intermediate",
  "presentationStyle": "educational",
  "context": {},
  "max_length": 4096,
  "temperature": 0.8
}
```

**Response:** Binary PDF file download

---

## 📊 Summary Table

| # | Method | Endpoint | Purpose | Returns |
|---|--------|----------|---------|---------|
| 1 | POST | `/orchestrate` | Complete presentation generation | JSON + base64 PPT |
| 2 | POST | `/slides` | Create slides only | JSON (deckId) |
| 3 | GET | `/slides/{deck_id}` | Get deck details | JSON |
| 4 | POST | `/slides/{deck_id}/export` | Export PPTX/PDF | Binary file |
| 5 | GET | `/slides/{deck_id}/download` | Download exported file | Binary file |
| 6 | POST | `/slides/{deck_id}/speaker-notes` | Generate speaker notes | PDF download |
| 7 | GET | `/slides/{deck_id}/speaker-notes/download` | Download notes PDF | PDF download |
| 8 | POST | `/slides/{deck_id}/quizzes` | Generate quiz | JSON or PDF |
| 9 | POST | `/generate-text` | Generate text only | JSON |
| 10 | POST | `/generate-image` | Generate image | JSON |
| 11 | POST | `/generate-diagram` | Generate diagram | JSON |
| 12 | POST | `/generate-slides` | Generate slides with media | JSON |
| 13 | POST | `/generate-media/{deck_id}` | Add media to deck | JSON |
| 14 | POST | `/generate-notes` | Generate standalone notes | PDF download |

---

## 🔧 Postman Setup Tips

1. **Base URL:** Set as environment variable: `{{base_url}}` = `http://localhost:8000`

2. **Common Headers:**
   - `Content-Type: application/json`

3. **Test Flow:**
   ```
   1. POST /orchestrate → Get deckId
   2. GET /slides/{deckId} → Verify deck
   3. POST /slides/{deckId}/export → Download PPTX
   4. POST /slides/{deckId}/quizzes?download=pdf → Download Quiz PDF
   ```

4. **Save deckId:** After `/orchestrate`, save `deckId` to a Postman variable for subsequent requests.

5. **PDF Downloads:** For PDF endpoints, set Postman to "Send and Download" to save files.

---

## ⚠️ Important Notes

- All `deck_id` values are MongoDB ObjectIds (24 hex characters)
- PDF export requires LibreOffice for best quality (falls back to ReportLab)
- Quiz generation requires `reportlab` library for PDF export
- Media generation is optional and won't fail the orchestration if it errors
- The `/orchestrate` endpoint does everything in one call (recommended for most use cases)

