# Quick Setup Guide for Running AI Service

## ✅ What Works Automatically (No Changes Needed)

- ✅ Ollama installation and model (`deepseek-r1:1.5b`) - installed automatically
- ✅ All Python dependencies - installed automatically  
- ✅ Templates - copied automatically
- ✅ All system tools (LibreOffice, Graphviz, etc.) - installed automatically
- ✅ API keys - defaults are baked in (but you can override)

## ⚙️ What You Need to Configure

### 1. MongoDB Connection (REQUIRED)

**Option A: MongoDB on your laptop (local)**
```bash
# Windows/Mac - use host.docker.internal
docker run --rm -p 8000:8000 \
  -e AI_MONGODB_URI="mongodb://host.docker.internal:27017" \
  -e AI_DB_NAME="ai_db" \
  ai-service

# Linux - use your host IP or Docker network
docker run --rm -p 8000:8000 \
  -e AI_MONGODB_URI="mongodb://172.17.0.1:27017" \
  -e AI_DB_NAME="ai_db" \
  ai-service
```

**Option B: MongoDB Atlas (cloud)**
```bash
docker run --rm -p 8000:8000 \
  -e AI_MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net" \
  -e AI_DB_NAME="ai_db" \
  ai-service
```

**Option C: MongoDB in another Docker container**
```bash
# Start MongoDB first
docker run -d --name mongodb -p 27017:27017 mongo

# Then run AI service (use same Docker network)
docker run --rm -p 8000:8000 \
  --link mongodb:mongodb \
  -e AI_MONGODB_URI="mongodb://mongodb:27017" \
  -e AI_DB_NAME="ai_db" \
  ai-service
```

### 2. API Keys (Optional - defaults are already set)

If you want to use your own API keys instead of the defaults:

```bash
docker run --rm -p 8000:8000 \
  -e AI_MONGODB_URI="mongodb://host.docker.internal:27017" \
  -e AI_DB_NAME="ai_db" \
  -e GEMINI_API_KEY="your_key_here" \
  -e STABILITY_API_KEY="your_key_here" \
  -e UNSPLASH_API_KEY="your_key_here" \
  ai-service
```

### 3. Using .env File (Easiest)

Create `ai/.env` file with your settings:

```env
AI_MONGODB_URI=mongodb://host.docker.internal:27017
AI_DB_NAME=ai_db
GEMINI_API_KEY=your_key_here
STABILITY_API_KEY=your_key_here
UNSPLASH_API_KEY=your_key_here
```

Then run:
```bash
docker run --rm -p 8000:8000 \
  --env-file ./ai/.env \
  ai-service
```

## 🚀 Complete Setup Steps

1. **Make sure MongoDB is running** (or use Atlas)
   ```bash
   # Check if MongoDB is running locally
   # Windows: Check Services
   # Mac/Linux: ps aux | grep mongod
   ```

2. **Build the Docker image** (one time)
   ```bash
   cd ai
   docker build -t ai-service .
   ```

3. **Run the container**
   ```bash
   docker run --rm -p 8000:8000 \
     -e AI_MONGODB_URI="mongodb://host.docker.internal:27017" \
     -e AI_DB_NAME="ai_db" \
     ai-service
   ```

4. **Test it**
   - Open http://localhost:8000/docs
   - Try the `/orchestrate` endpoint

## 🔍 Troubleshooting

**MongoDB connection fails:**
- Check if MongoDB is running: `docker ps` or check services
- Try `host.docker.internal` instead of `localhost` (Windows/Mac)
- On Linux, use your actual host IP address

**Ollama not working:**
- Check logs: `docker logs <container_id>`
- Ollama should start automatically inside container
- Model will be pulled on first run (takes a few minutes)

**Port already in use:**
- Change port: `-p 8001:8000` (maps host 8001 to container 8000)

## 📝 Summary

**Minimum change needed:** Just set `AI_MONGODB_URI` to point to your MongoDB!

Everything else (Ollama, models, templates, dependencies) works automatically. 🎉

