#!/bin/bash
set -e

# Start Ollama service in background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 3

# Pull the model if not already available
echo "Ensuring Ollama model ${OLLAMA_MODEL:-deepseek-r1:1.5b} is available..."
ollama pull ${OLLAMA_MODEL:-deepseek-r1:1.5b} || echo "Model pull skipped or already available"

# Start FastAPI
echo "Starting FastAPI server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000

