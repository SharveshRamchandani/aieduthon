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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Ensure output directories exist for static media served at /media
RUN mkdir -p /app/src/out/generated_images /app/src/out/generated_diagrams

WORKDIR /app/src


ARG AI_MONGODB_URI_ARG="mongodb://localhost:27017"
ARG AI_DB_NAME_ARG="ai_db"
ARG HF_API_KEY_ARG=""
ARG LLM_PROVIDER_ARG="huggingface"
ARG STABILITY_API_KEY_ARG="sk-oCnyzT2dyrctVNx0Qdi9CKVXOAQf1GbLYb7FSM5qK0xosprr"
ARG GEMINI_API_KEY_ARG="AIzaSyC2nF_tsiQ1WxPZWxeucIBB2dlKxkDsROI"
ARG UNSPLASH_API_KEY_ARG="IybtH3gfW4geFaKGGUUNeI-XxwucxNBSy-uTDkuxkbc"

ENV AI_MONGODB_URI=${AI_MONGODB_URI_ARG} \
    AI_DB_NAME=${AI_DB_NAME_ARG} \
    HF_API_KEY=${HF_API_KEY_ARG} \
    LLM_PROVIDER=${LLM_PROVIDER_ARG} \
    STABILITY_API_KEY=${STABILITY_API_KEY_ARG} \
    GEMINI_API_KEY=${GEMINI_API_KEY_ARG} \
    UNSPLASH_API_KEY=${UNSPLASH_API_KEY_ARG}

EXPOSE 8000

# Default command: run FastAPI with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

