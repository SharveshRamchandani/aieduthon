# Quick Setup & Run Guide

## Step 1: Install Python Dependencies

```bash
cd ai/src
pip install -r requirements.txt
```

**Note:** If you get errors with `bitsandbytes`, you can skip it (it's only needed for quantization on GPU):
```bash
pip install -r requirements.txt --ignore-installed bitsandbytes
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the `ai/` directory (NOT in `ai/src/`):

```env
# MongoDB Configuration
AI_MONGODB_URI=mongodb://localhost:27017
AI_DB_NAME=ai_db

# Gemini API Configuration (REQUIRED for text generation)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_ID=gemini-2.5-flash

# Optional: Image Generation (Stability AI)
STABILITY_API_KEY=your_stability_key_here

# Optional: Provider setting (defaults to gemini)
LLM_PROVIDER=gemini
```

**Get your Gemini API key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy it to your `.env` file as `GEMINI_API_KEY`

**Note:** The `.env` file should be in the `ai/` directory (same level as `src/`), not inside `src/`.

**If you don't have MongoDB running locally**, you can use MongoDB Atlas (free tier):
```env
AI_MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
AI_DB_NAME=ai_db
```

## Step 3: Initialize Database (First Time Only)

```bash
cd ai/src
python init_db.py
```

## Step 4: Run the API Server

**Option 1: Direct uvicorn command (recommended)**
```bash
cd ai/src
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 2: Using the Python script**
```bash
cd ai/src
python run_api.py
```

The API will start at: **http://localhost:8000**

## Step 5: Test It

Open your browser and go to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/

Or test with curl:
```bash
curl -X POST "http://localhost:8000/generate-text" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain photosynthesis", "context": {"grade_level": "10th"}}'
```

## Troubleshooting

### MongoDB Not Running?
- **Windows:** Download MongoDB Community Server from mongodb.com
- **Mac:** `brew install mongodb-community`
- **Linux:** `sudo apt-get install mongodb`

Or use MongoDB Atlas (cloud, free tier).

### Model Download Issues?
First run will download the Mistral model (~13GB). Make sure you have:
- Good internet connection
- Enough disk space
- Patience (can take 10-30 minutes)

### Port 8000 Already in Use?
Edit `run_api.py` and change the port:
```python
uvicorn.run("api.main:app", host="0.0.0.0", port=8001, reload=True)
```

### Still Having Issues?
Check the console output for error messages. The API will show detailed errors.

