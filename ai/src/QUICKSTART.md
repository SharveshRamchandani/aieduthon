# Quick Start Guide - Multimodal AI Pipeline

## Setup

### 1. Install Dependencies

```bash
cd ai/src
pip install -r requirements.txt
```

### 2. Install System Dependencies

**Graphviz (for diagrams):**
- Ubuntu/Debian: `sudo apt-get install graphviz`
- macOS: `brew install graphviz`
- Windows: Download from https://graphviz.org/download/

### 3. Configure Environment

Create `.env` file in `ai/` directory:

```env
AI_MONGODB_URI=mongodb://localhost:27017
AI_DB_NAME=ai_db
HF_API_KEY=your_huggingface_token  # Optional, for private models
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Configure Models

Edit `config/model_registry.yaml` to select models:

```yaml
models:
  text:
    active_model: "meta-llama/Llama-2-7b-chat-hf"  # Change if needed
  image:
    active_model: "stabilityai/stable-diffusion-2-1"  # Change if needed
```

## Usage

### Start API Server

```bash
python run_api.py
```

API will be available at `http://localhost:8000`

### Generate Complete Presentation

```bash
curl -X POST "http://localhost:8000/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a presentation about Photosynthesis for 10th grade students",
    "userId": "user123",
    "locale": "en",
    "context": {
      "grade_level": "10th",
      "subject": "biology"
    },
    "generate_images": true,
    "generate_diagrams": true
  }'
```

### Generate Text Only

```bash
curl -X POST "http://localhost:8000/generate-text" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain photosynthesis in simple terms",
    "context": {
      "grade_level": "10th",
      "subject": "biology"
    }
  }'
```

### Generate Image

```bash
curl -X POST "http://localhost:8000/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Educational illustration of photosynthesis process",
    "width": 1024,
    "height": 768
  }'
```

### Generate Diagram

```bash
curl -X POST "http://localhost:8000/generate-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_type": "cycle",
    "description": "Photosynthesis cycle showing conversion of sunlight to glucose"
  }'
```

## Python Usage

### Basic Text Generation

```python
from agents.text_generation_agent import TextGenerationAgent

agent = TextGenerationAgent()
result = agent.generate(
    prompt="Explain photosynthesis",
    context={"grade_level": "10th"}
)
print(result["text"])
```

### Complete Slide Generation

```python
from agents.prompt_to_slide_agent import PromptToSlideAgent

agent = PromptToSlideAgent()
result = agent.generate_slides(
    prompt_text="Create a presentation about Photosynthesis",
    user_id="user123",
    locale="en",
    context={
        "grade_level": "10th",
        "subject": "biology",
        "generate_media": True
    }
)
print(f"Deck ID: {result['deck_id']}")
```

## Model Switching

To switch models, edit `config/model_registry.yaml`:

```yaml
models:
  text:
    active_model: "mistralai/Mistral-7B-Instruct-v0.2"  # Switch model
```

No code changes needed! Models are loaded dynamically.

## Quantization (Memory Optimization)

Enable quantization in `config/model_registry.yaml`:

```yaml
models:
  text:
    quantization:
      enabled: true
      load_in_8bit: true  # Reduces memory by ~50%
```

## Troubleshooting

### Model Download
First run will download models (can be large, 4-13GB). Ensure good internet connection.

### GPU Memory
If out of memory:
1. Enable quantization (8-bit)
2. Use smaller models (7B instead of 13B)
3. Use CPU mode (slower but works)

### Graphviz Issues
If diagram generation fails:
1. Install Graphviz system package
2. Check PATH includes Graphviz bin directory
3. Use Matplotlib as fallback

### Database Connection
Ensure MongoDB is running:
```bash
mongod
```

## Next Steps

1. Read `MULTIMODAL_IMPLEMENTATION.md` for detailed documentation
2. Read `MULTIMODAL_ARCHITECTURE.md` for architecture overview
3. Explore API documentation at `http://localhost:8000/docs`
4. Customize models in `config/model_registry.yaml`

## Support

Check logs for detailed error messages. All agents have fallback mechanisms if LLM fails.

