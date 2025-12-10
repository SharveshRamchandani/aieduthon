# Ollama Setup Guide for Deepseek-R1:1.5b

This guide will help you set up Ollama and the deepseek-r1:1.5b model for the content expansion pipeline.

## Overview

The pipeline uses **deepseek-r1:1.5b** running on Ollama for the **3rd pass** (content expansion). This happens after:
1. **Pass 1 (Gemini)**: Prompt analysis
2. **Pass 2 (Gemini)**: Initial slide generation
3. **Pass 3 (Deepseek)**: Content expansion and keyword elaboration

## Step 1: Install Ollama

### Windows
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically as a service

### macOS
```bash
brew install ollama
# Or download from: https://ollama.com/download/mac
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Step 2: Verify Ollama is Running

### Check if Ollama is running:
```bash
# Test the API
curl http://localhost:11434/api/tags
```

Or use the test script:
```bash
cd ai/src
python test_ollama_connection.py
```

### If Ollama is not running:

**Windows:**
- Ollama should run as a service automatically
- If not, open Command Prompt and run: `ollama serve`
- Or check Windows Services for "Ollama"

**macOS/Linux:**
```bash
# Start Ollama in terminal
ollama serve

# Or run as background service
ollama serve &
```

## Step 3: Pull the Deepseek Model

The model needs to be downloaded to your local Ollama instance:

```bash
ollama pull deepseek-r1:1.5b
```

This will download ~1.1GB. The first time may take a few minutes depending on your internet speed.

### Verify the model is available:
```bash
ollama list
```

You should see `deepseek-r1:1.5b` in the list.

## Step 4: Test the Connection

Run the test script to verify everything is working:

```bash
cd ai/src
python test_ollama_connection.py
```

Expected output:
```
============================================================
Ollama Connection & Deepseek Model Test
============================================================

Step 1: Checking if Ollama is running...
✅ Ollama is running!

Step 2: Checking if deepseek-r1:1.5b model is available...
✅ Found model: deepseek-r1:1.5b

🧪 Testing model generation...
✅ Model generation test successful!
   Response: Hello, Ollama is working!...

============================================================
✅ All checks passed! Ollama is ready to use.
============================================================
```

## Step 5: Configuration

The model is already configured in `ai/src/config/model_registry.yaml`:

```yaml
- name: "deepseek-r1:1.5b"
  provider: "ollama"
  ollama_model: "deepseek-r1:1.5b"
  ollama_base_url: "http://localhost:11434"
```

**No changes needed** - the code automatically uses this configuration for the 3rd pass.

## Troubleshooting

### Error: "Could not connect to Ollama"

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check if port 11434 is available: `netstat -an | grep 11434` (Linux/Mac) or check Windows ports
3. Verify the URL in `model_registry.yaml` matches your Ollama instance

### Error: "Model not found"

**Solution:**
```bash
# Pull the model
ollama pull deepseek-r1:1.5b

# Verify it's available
ollama list
```

### Error: "Connection timeout"

**Solution:**
- Check if Ollama is responding: `curl http://localhost:11434/api/tags`
- Restart Ollama: Stop the service and run `ollama serve` again
- Check firewall settings if using a different machine

### Model is slow

The deepseek-r1:1.5b model is optimized for CPU and should run reasonably fast. If it's too slow:
- Make sure you have enough RAM (model needs ~2GB)
- Close other heavy applications
- Consider using a GPU-enabled Ollama build (if you have a compatible GPU)

## How It Works in the Pipeline

1. **User submits prompt** → Pass 1 (Gemini) analyzes it
2. **Gemini generates initial slides** → Pass 2 (Gemini) creates structure
3. **Deepseek expands content** → Pass 3 (Deepseek via Ollama) elaborates keywords
4. **Content is placed in PPT** → Image placeholders preserved

The expansion happens in `expand_slide_content()` method, which:
- Takes the JSON from Pass 2
- Sends it to deepseek-r1:1.5b via Ollama API
- Expands bullets and notes while preserving image placeholders
- Returns enriched content for PPT generation

## Manual Testing

You can test Ollama directly:

```bash
# Test the model
ollama run deepseek-r1:1.5b "Say hello"

# Or via API
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:1.5b",
  "prompt": "Say hello",
  "stream": false
}'
```

## Next Steps

Once Ollama is set up and tested:
1. ✅ Run `python test_ollama_connection.py` to verify
2. ✅ Start your API server: `python run_api.py`
3. ✅ Test the full pipeline with a prompt
4. ✅ Check logs to see deepseek being used in Pass 3

The pipeline will automatically use deepseek-r1:1.5b for content expansion - no code changes needed!

