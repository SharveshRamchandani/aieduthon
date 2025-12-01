# Multimodal AI Pipeline Implementation

## Overview

This implementation provides a **modular, plug-and-play multimodal AI pipeline** for educational slide/lesson generation using Hugging Face models.

## Architecture

### 1. Model Registry (`config/model_registry.yaml`)
- Centralized configuration for all models
- Easy model switching without code changes
- Supports quantization for memory efficiency
- Configurable generation parameters

### 2. Model Manager (`agents/model_manager.py`)
- Dynamic model loading with caching
- Quantization support (8-bit, 4-bit)
- Device management (auto, CPU, CUDA)
- Model switching at runtime

### 3. Agent Architecture

#### Text Generation Agent (`agents/text_generation_agent.py`)
- Uses Hugging Face LLMs (Llama, Mistral, Falcon)
- Intelligent prompt formatting per model
- Caching for performance
- JSON response parsing

#### Image Generation Agent (`agents/image_generation_agent.py`)
- Uses Stable Diffusion models
- Educational context enhancement
- Automatic image captioning (BLIP)
- Media storage and management

#### Diagram Generation Agent (`agents/diagram_generation_agent.py`)
- Graphviz for flowcharts/processes
- Matplotlib for charts/plots
- LLM-assisted diagram structuring
- Multiple diagram types (flowchart, hierarchy, cycle, chart)

#### Media Integration Agent (`agents/media_integration_agent.py`)
- Orchestrates image and diagram generation
- Automatic media-to-slide matching
- Smart diagram type detection
- Media suggestion system

### 4. Updated Agents

#### PromptToSlideAgent
- Now uses LLM for prompt analysis
- LLM-based content generation
- Automatic media generation integration
- Fallback to heuristics if LLM fails

#### QuizGenerationAgent
- LLM-based question generation
- Contextual question creation
- Multiple question types (MCQ, True/False, Fill-in-the-blank)

#### SpeakerNotesAgent
- LLM-generated speaker notes
- Audience-aware content
- Comprehensive note structure

## API Endpoints

### New Multimodal Endpoints

1. **POST /generate-text**
   - Generate text using LLM
   - Parameters: prompt, context, max_length, temperature

2. **POST /generate-image**
   - Generate image using Stable Diffusion
   - Parameters: prompt, width, height, num_images

3. **POST /generate-diagram**
   - Generate diagram using visualization tools
   - Parameters: diagram_type, description, format

4. **POST /generate-slides**
   - Complete slide generation with media
   - Parameters: prompt, userId, locale, generate_images, generate_diagrams

5. **POST /generate-media/{deck_id}**
   - Generate media for existing deck
   - Parameters: generate_images, generate_diagrams

### Updated Orchestration

**POST /orchestrate**
- Now includes multimodal generation
- Generates slides, notes, quizzes, images, and diagrams
- All in one endpoint

## Usage Examples

### 1. Generate Text
```python
from agents.text_generation_agent import TextGenerationAgent

agent = TextGenerationAgent()
result = agent.generate(
    prompt="Explain photosynthesis for 10th grade students",
    context={"grade_level": "10th", "subject": "biology"}
)
print(result["text"])
```

### 2. Generate Image
```python
from agents.image_generation_agent import ImageGenerationAgent

agent = ImageGenerationAgent()
result = agent.generate(
    prompt="Educational illustration of photosynthesis process",
    width=1024,
    height=768
)
print(result["urls"])
```

### 3. Generate Diagram
```python
from agents.diagram_generation_agent import DiagramGenerationAgent

agent = DiagramGenerationAgent()
result = agent.generate(
    diagram_type="cycle",
    description="Photosynthesis cycle showing conversion of sunlight to glucose"
)
print(result["file_path"])
```

### 4. Generate Complete Slides
```python
from agents.prompt_to_slide_agent import PromptToSlideAgent

agent = PromptToSlideAgent()
result = agent.generate_slides(
    prompt_text="Create a presentation about Photosynthesis for 10th grade",
    user_id="user123",
    locale="en",
    context={
        "grade_level": "10th",
        "subject": "biology",
        "generate_media": True
    }
)
print(result["deck_id"])
```

## Model Configuration

### Switching Models

Edit `config/model_registry.yaml`:

```yaml
models:
  text:
    active_model: "meta-llama/Llama-2-7b-chat-hf"  # Change this
  image:
    active_model: "stabilityai/stable-diffusion-2-1"  # Change this
```

### Available Text Models
- `meta-llama/Llama-2-7b-chat-hf` (default)
- `meta-llama/Llama-2-13b-chat-hf`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `tiiuae/falcon-7b-instruct`

### Available Image Models
- `stabilityai/stable-diffusion-2-1` (default)
- `runwayml/stable-diffusion-v1-5`

### Quantization

Enable quantization in `model_registry.yaml`:

```yaml
quantization:
  enabled: true
  load_in_8bit: true
  load_in_4bit: false
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies:
```bash
# For Graphviz (diagrams)
# Ubuntu/Debian:
sudo apt-get install graphviz

# macOS:
brew install graphviz

# Windows:
# Download from: https://graphviz.org/download/
```

3. Set up environment variables:
```bash
# .env file
AI_MONGODB_URI=mongodb://localhost:27017
AI_DB_NAME=ai_db
HF_API_KEY=your_huggingface_token  # Optional, for private models
```

4. Initialize database:
```bash
python init_db.py
```

## Caching

All generated content is cached in MongoDB:
- Text generation: Cached by prompt hash
- Image generation: Cached by prompt + dimensions
- Cache TTL: Configurable (default 1 hour for text, 24 hours for images)

## Feedback System

Store user feedback for model improvement:

```python
from agents.text_generation_agent import TextGenerationAgent

agent = TextGenerationAgent()
agent.store_feedback(
    prompt="...",
    generated_text="...",
    rating=5,
    feedback="Great content!",
    user_id="user123"
)
```

## Performance Optimization

1. **Model Caching**: Models are loaded once and reused
2. **Result Caching**: Generated content is cached
3. **Quantization**: Reduces memory usage by 50-75%
4. **Batch Processing**: Support for batch generation (future)

## Error Handling

- All agents have fallback mechanisms
- If LLM fails, falls back to heuristic methods
- Media generation is optional (won't fail entire request)
- Comprehensive error logging

## Database Structure

### Collections
- `prompts`: User prompts
- `slides`: Generated slide decks
- `media`: Generated images
- `diagrams`: Generated diagrams
- `quizzes`: Generated quizzes
- `ai_cache`: Cached AI results
- `ai_feedback`: User feedback

## Future Enhancements

1. **Batch Generation**: Generate multiple slides/images in parallel
2. **Model Fine-tuning**: Fine-tune models on user feedback
3. **Multi-language Support**: Better multilingual generation
4. **Video Generation**: Generate educational videos
5. **Voice Generation**: Generate narration for slides
6. **Interactive Diagrams**: Interactive HTML diagrams
7. **Real-time Generation**: WebSocket support for real-time updates

## Troubleshooting

### Model Loading Issues
- Check GPU availability: `torch.cuda.is_available()`
- Reduce model size or enable quantization
- Use CPU if GPU not available

### Memory Issues
- Enable quantization (8-bit or 4-bit)
- Use smaller models
- Unload unused models: `model_manager.unload_model("text")`

### Diagram Generation Issues
- Install Graphviz system package
- Check Graphviz path in environment
- Use Matplotlib as fallback

### Image Generation Issues
- Check GPU memory (Stable Diffusion needs ~4GB VRAM)
- Reduce image resolution
- Use CPU mode (slower but works)

## Support

For issues or questions, check:
1. Model registry configuration
2. Database connection
3. Model download (first run downloads models)
4. Log files for detailed error messages

