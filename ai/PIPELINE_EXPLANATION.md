# Pipeline Architecture & Multimodal Capabilities

## Overview

Yes, this **IS a multimodal pipeline** that generates educational presentations with text, images, and diagrams.

## Complete Pipeline Flow

```
User Input (Text Prompt)
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Prompt Analysis (Gemini - Pass 1)              │
│ - Analyzes subject, complexity, topics                  │
│ - Estimates slide count                                  │
│ - Determines target audience                            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Initial Slide Generation (Gemini - Pass 2)     │
│ - Generates slide structure with short bullets          │
│ - Creates titles, initial content                       │
│ - Adds image placeholders                               │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Content Expansion (Deepseek-R1:1.5b - Pass 3) │
│ - Expands keywords into full sentences                 │
│ - Elaborates bullets for PPT readability               │
│ - Preserves image placeholders                          │
│ - Uses Ollama API (local)                              │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Template Selection                            │
│ - Selects appropriate PPT template                     │
│ - Based on subject, audience, style                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Media Generation (Multimodal)                 │
│ ├─→ Image Generation Agent                            │
│ │   - Generates educational images per slide          │
│ │   - Uses Stability AI API or HuggingFace            │
│ │   - Auto-captions with BLIP                         │
│ │   - Stores in MongoDB                                │
│ │                                                      │
│ └─→ Diagram Generation Agent                           │
│     - Detects diagram type needed                     │
│     - Generates with Graphviz/Matplotlib              │
│     - Creates flowcharts, cycles, charts              │
│     - Stores in MongoDB                                │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Speaker Notes Generation                       │
│ - Generates detailed speaker notes                    │
│ - Audience-aware content                               │
│ - Comprehensive talking points                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 7: Quiz Generation                               │
│ - Creates quiz questions                               │
│ - Multiple question types (MCQ, True/False)            │
│ - Contextual to slide content                          │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 8: PPT Export                                     │
│ - Combines all content into PowerPoint                 │
│ - Inserts generated images                             │
│ - Adds diagrams                                         │
│ - Applies template styling                             │
│ - Validates output                                      │
└─────────────────────────────────────────────────────────┘
    ↓
Final Presentation (PPTX file)
```

## Multimodal Components

### 1. **Text Generation** (3 Passes)
- **Pass 1 (Gemini)**: Prompt analysis
- **Pass 2 (Gemini)**: Initial slide structure
- **Pass 3 (Deepseek-R1:1.5b via Ollama)**: Content expansion

### 2. **Image Generation**
- **Agent**: `ImageGenerationAgent`
- **Models**: 
  - Stability AI API (primary)
  - HuggingFace Stable Diffusion (fallback)
  - Local Stable Diffusion (fallback)
- **Features**:
  - Educational context enhancement
  - Auto-captioning with BLIP
  - Per-slide image generation
  - Caching for performance

### 3. **Diagram Generation**
- **Agent**: `DiagramGenerationAgent`
- **Tools**:
  - Graphviz (flowcharts, process diagrams)
  - Matplotlib (charts, data visualization)
  - Mermaid (sequence diagrams)
- **Types**:
  - Flowcharts
  - Hierarchies
  - Cycles
  - Charts
  - Generic diagrams

### 4. **Media Integration**
- **Agent**: `MediaIntegrationAgent`
- **Responsibilities**:
  - Orchestrates image + diagram generation
  - Matches visuals to slide content
  - Ensures visual coherence
  - Handles media storage

## API Endpoint: `/orchestrate`

The main entry point that coordinates everything:

```python
POST /orchestrate
{
  "prompt": "Create a presentation about Photosynthesis",
  "userId": "user123",
  "locale": "en",
  "context": {
    "grade_level": "10th",
    "subject": "biology"
  },
  "generate_images": true,    # Enable image generation
  "generate_diagrams": true,  # Enable diagram generation
  "estimated_slides": 10
}
```

**Response:**
```json
{
  "deckId": "...",
  "promptId": "...",
  "quizIds": [...],
  "mediaGenerated": true,
  "pptFile": "base64...",
  "pptFilename": "presentation.pptx",
  "pptValidation": {...}
}
```

## Data Flow

### Text Processing
1. **Input**: User prompt text
2. **Processing**: 3 LLM passes (2x Gemini, 1x Deepseek)
3. **Output**: Structured slide content with expanded text

### Image Processing
1. **Input**: Slide content + image placeholders
2. **Processing**: Image generation per slide
3. **Output**: Generated images stored in MongoDB, linked to slides

### Diagram Processing
1. **Input**: Slide content (detects diagram needs)
2. **Processing**: Diagram generation based on content type
3. **Output**: Diagrams stored in MongoDB, linked to slides

### Final Assembly
1. **Input**: All generated content (text, images, diagrams)
2. **Processing**: PPT export with template
3. **Output**: Complete PowerPoint file

## Storage Architecture

All content is stored in MongoDB:

```
MongoDB Collections:
├── prompts          → User prompts
├── slides           → Generated slide decks
├── media            → Generated images
├── diagrams         → Generated diagrams
├── quizzes          → Generated quizzes
├── ai_cache         → Cached AI results
├── ai_sessions      → Generation sessions
└── ai_outputs       → Output logging
```

## Key Features

### ✅ Multimodal Generation
- **Text**: LLM-based content generation (3 passes)
- **Images**: AI-generated educational images
- **Diagrams**: Programmatically generated visualizations

### ✅ Intelligent Orchestration
- Sequential pipeline execution
- Error recovery with fallbacks
- Optional media generation
- Context-aware generation

### ✅ Performance Optimization
- Caching at multiple levels
- Session-based context
- Lazy model loading
- Parallel media generation

### ✅ Flexibility
- Multiple model providers
- Configurable via YAML
- Runtime model switching
- Template selection

## Example: Photosynthesis Presentation

**Input:**
```
"Create a presentation about Photosynthesis for 10th grade"
```

**Output:**
- **10 slides** with expanded content
- **10 images** (one per slide) - plants, sunlight, chloroplasts
- **2-3 diagrams** - photosynthesis cycle, plant structure
- **Speaker notes** for each slide
- **Quiz questions** related to content
- **Complete PPTX file** ready to use

## Model Configuration

Models are configured in `config/model_registry.yaml`:

```yaml
models:
  text:
    active_model: "gemma-3-1b-it"  # Gemini API
    available_models:
      - name: "deepseek-r1:1.5b"   # Ollama (for Pass 3)
        provider: "ollama"
        ollama_model: "deepseek-r1:1.5b"
        ollama_base_url: "http://localhost:11434"
  
  image:
    active_model: "stabilityai/stable-diffusion-xl"
    source: "stock"  # or "generate"
```

## Why Multimodal?

1. **Better Learning**: Visual + text = multiple learning styles
2. **Engagement**: Images and diagrams increase student engagement
3. **Comprehension**: Complex concepts easier to understand visually
4. **Quality**: Professional-looking presentations
5. **Automation**: No manual image/diagram insertion needed

## Current Status

✅ **Fully Implemented:**
- Text generation (3 passes)
- Image generation
- Diagram generation
- Media integration
- PPT export
- Quiz generation
- Speaker notes

✅ **Working:**
- Gemini API integration
- Deepseek-R1:1.5b via Ollama
- Stability AI image generation
- Graphviz diagram generation
- MongoDB storage
- Caching system

## Summary

**Yes, this is a multimodal pipeline** that:
- Processes text through 3 LLM passes
- Generates images for each slide
- Creates diagrams when appropriate
- Integrates all media into final PPT
- Provides complete educational presentations

The pipeline is production-ready and handles the full multimodal workflow from prompt to complete presentation.

