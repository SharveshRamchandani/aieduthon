FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps: build tools (for some python wheels), libs for PIL/vision, PDF export, diagrams
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        libgl1 \
        libglib2.0-0 \
        libreoffice \
        graphviz \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        fonts-dejavu-core \
        ffmpeg \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama for local model inference
# Note: This installs Ollama inside the container. For host-based Ollama, 
# set OLLAMA_BASE_URL to http://host.docker.internal:11434 instead
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the default Ollama model (deepseek-r1:1.5b) during build
# Comment this out if you want to pull models at runtime instead
RUN ollama pull deepseek-r1:1.5b || echo "Ollama model pull skipped (will pull at runtime)"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source (includes templates in "ppt dataset" folder)
COPY src/ ./src/

# Verify templates are copied (optional check - will warn if missing)
RUN if [ ! -d "/app/src/ppt dataset" ]; then echo "WARNING: Template folder 'ppt dataset' not found!"; fi

# Ensure output directories exist for static media served at /media
RUN mkdir -p /app/src/out/generated_images /app/src/out/generated_diagrams

# Copy startup script for running Ollama + FastAPI
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app/src


ARG AI_MONGODB_URI_ARG="mongodb://localhost:27017"
ARG AI_DB_NAME_ARG="ai_db"
ARG HF_API_KEY_ARG=""
ARG LLM_PROVIDER_ARG="huggingface"
ARG STABILITY_API_KEY_ARG="sk-oCnyzT2dyrctVNx0Qdi9CKVXOAQf1GbLYb7FSM5qK0xosprr"
ARG GEMINI_API_KEY_ARG="AIzaSyC2nF_tsiQ1WxPZWxeucIBB2dlKxkDsROI"
ARG UNSPLASH_API_KEY_ARG="IybtH3gfW4geFaKGGUUNeI-XxwucxNBSy-uTDkuxkbc"
ARG OLLAMA_BASE_URL_ARG="http://localhost:11434"
ARG OLLAMA_MODEL_ARG="deepseek-r1:1.5b"

ENV AI_MONGODB_URI=${AI_MONGODB_URI_ARG} \
    AI_DB_NAME=${AI_DB_NAME_ARG} \
    HF_API_KEY=${HF_API_KEY_ARG} \
    LLM_PROVIDER=${LLM_PROVIDER_ARG} \
    STABILITY_API_KEY=${STABILITY_API_KEY_ARG} \
    GEMINI_API_KEY=${GEMINI_API_KEY_ARG} \
    UNSPLASH_API_KEY=${UNSPLASH_API_KEY_ARG} \
    OLLAMA_BASE_URL=${OLLAMA_BASE_URL_ARG} \
    OLLAMA_MODEL=${OLLAMA_MODEL_ARG}

EXPOSE 8000 11434

# Start Ollama service in background, then run FastAPI
# Note: Ollama runs on port 11434 inside container
# Use startup script to manage both services
CMD ["/app/start.sh"]

