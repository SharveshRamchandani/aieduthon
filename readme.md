# AIEduthon - AI-Powered Educational Presentation Generator

## Overview

AIEduthon is a comprehensive multimodal AI system that automatically generates educational presentations from text prompts. The platform creates complete slide decks with personalized content, relevant images, diagrams, speaker notes, and quizzes tailored to different educational levels and audiences.

The system uses advanced AI models to understand teacher prompts, generate structured content, integrate multimedia elements, and export professional PowerPoint presentations. It supports multiple languages, various educational levels, and customizable presentation styles.

### Key Highlights

- **Multimodal AI Pipeline**: Seamlessly integrates text, images, and diagrams
- **Multiple AI Models**: Supports Gemini, Ollama (local), HuggingFace, and Stability AI
- **Smart Content Generation**: Three-pass generation pipeline for high-quality content
- **Professional Export**: PPTX and PDF export with template preservation
- **Comprehensive Features**: Speaker notes, quizzes, and multi-language support

## Architecture

The application consists of three main components:

### Backend Services

Python FastAPI Service (Port 8000)
- Handles AI-powered content generation
- Manages slide deck creation and export
- Provides RESTful API endpoints
- Integrates with multiple AI models and image services
- Supports local model inference via Ollama
- Three-pass content generation pipeline (Gemini → Gemini → Deepseek)

Go Authentication Service
- Manages user authentication via Google OAuth
- Handles user sessions and authorization
- Provides secure API endpoints for user management

### Frontend Application

React TypeScript Application (Port 5173)
- Modern web interface built with React and TypeScript
- Uses shadcn-ui components and Tailwind CSS 
- Provides intuitive UI for creating and editing presentations
- Supports real-time preview and editing

### Database

MongoDB Database
- Stores prompts, slide decks, media, quizzes, and user data
- Maintains generation history and caching
- Supports text search and indexing

## Multimodal AI Pipeline

The system uses a sophisticated three-pass generation pipeline:

```
User Prompt
    ↓
┌─────────────────────────────────────┐
│ Pass 1: Prompt Analysis (Gemini)  │
│ - Analyzes subject & complexity     │
│ - Estimates slide count             │
│ - Determines target audience        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Pass 2: Initial Generation (Gemini)│
│ - Creates slide structure            │
│ - Generates titles & keywords       │
│ - Adds image placeholders           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Pass 3: Content Expansion (Deepseek)│
│ - Expands keywords to full content  │
│ - Elaborates bullets                │
│ - Preserves image placeholders      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Media Integration                   │
│ - Stock images (Unsplash/Pexels)    │
│ - AI-generated images (Stable Diff) │
│ - Diagrams (Graphviz/Matplotlib)    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Export & Validation                 │
│ - PPTX generation                    │
│ - PDF conversion (LibreOffice)       │
│ - Content validation                 │
└─────────────────────────────────────┘
```

## Key Features

### Content Generation

**Three-Pass Generation Pipeline**
- **Pass 1 (Gemini)**: Prompt analysis and subject matter understanding
- **Pass 2 (Gemini)**: Initial slide structure generation with keywords
- **Pass 3 (Deepseek via Ollama)**: Content expansion and keyword elaboration
- Ensures high-quality, detailed slide content

**Personalized Slide Creation**
- Converts text prompts into structured slide decks
- Analyzes subject matter and complexity automatically
- Generates appropriate number of slides based on content
- Creates logical sections and organization
- LLM-powered content generation with fallback mechanisms

**Audience Adaptation**
- Adjusts content for different grade levels
- Supports school, college, training, and professional audiences
- Modifies language complexity and tone
- Provides age-appropriate examples
- Context-aware content personalization

**Multi-language Support**
- English (en)
- Hindi (hi)
- Tamil (ta)
- Culturally relevant content generation
- Language-specific formatting and examples

### Media Integration

**Stock Image Integration**
- Automatically fetches relevant images from Unsplash, Pexels, and Pixabay
- Semantic search based on slide content
- Context-aware image selection
- Multiple image providers for redundancy
- Automatic fallback if one provider fails

**AI Image Generation**
- Generates custom educational images using Stable Diffusion
- Multiple providers: Stability AI API, HuggingFace API, Local Stable Diffusion
- Creates context-specific illustrations
- Supports various image styles and formats
- Auto-captioning with BLIP model
- Caching system for performance optimization

**Diagram Generation**
- Automatically creates flowcharts, process diagrams, and visualizations
- Uses Graphviz and Matplotlib for diagram creation
- Supports multiple diagram types:
  - Flowcharts (process flows, decision trees)
  - Hierarchy diagrams (organizational charts, taxonomies)
  - Cycle diagrams (life cycles, circular processes)
  - Charts and graphs (data visualizations)
  - Generic educational diagrams
- LLM-assisted diagram type detection
- Slide-specific diagram generation

### AI Model Support

**Text Generation Models**
- **Google Gemini API** (Primary): Used for prompt analysis and initial slide generation
  - Models: gemini-2.5-flash, gemini-2.5-flash-lite
  - Fast response times, high-quality content
- **Ollama with Deepseek-R1:1.5b** (Local): Used for content expansion
  - Runs locally for privacy and cost efficiency
  - Optimized for keyword expansion and content elaboration
- **HuggingFace API** (Fallback): Alternative text generation provider
  - Multiple model options available
  - Automatic fallback if primary providers fail

**Image Generation Models**
- **Stability AI API**: High-quality image generation
  - Stable Diffusion models
  - Educational image optimization
- **HuggingFace API**: Alternative image generation
  - Multiple model support
  - Cost-effective option
- **Local Stable Diffusion**: On-device image generation
  - Privacy-focused option
  - No API costs

**Diagram Generation Tools**
- **Graphviz**: Flowcharts, hierarchies, process diagrams
- **Matplotlib**: Charts, graphs, data visualizations
- **LLM-Assisted**: Automatic diagram type detection

### Additional Features

Speaker Notes Generation
- Creates comprehensive speaker notes for each slide
- Includes main points, timing notes, and engagement tips
- Adapts to audience level and presentation style
- Exports as PDF documents

Quiz Generation
- Generates quizzes from slide content
- Multiple question types: MCQ, True/False, Fill-in-the-blank
- Supports comprehensive, per-topic, and final-only quiz types
- Customizable number of questions
- PDF export capability

Template Selection
- Multiple presentation templates available
- Automatic template selection based on content
- Supports various styles: academic, business, creative, minimalist
- Smart slide management: Automatically removes unused template slides
- Preserves important conclusion slides (Thank You, Questions, etc.)
- Adaptive slide count: Adjusts to your content needs while keeping template structure

**PowerPoint Export**
- Exports complete presentations as PPTX files
- Integrates images and diagrams into slides
- Maintains proper formatting and layout
- Validates content quality (JSON token detection, bullet overflow checks)
- Stores PPT files in database for easy retrieval
- Base64 encoding for API responses

**PDF Export**
- Supports both PPTX and PDF export formats
- **LibreOffice-based conversion** (preserves templates, formatting, and design)
- Automatic fallback to ReportLab if LibreOffice unavailable
- Preserves all visual elements: fonts, colors, layouts, images
- Professional formatting for speaker notes and quizzes

## Project Structure

```
aieduthon/
├── ai/                          # Python AI backend
│   ├── src/
│   │   ├── agents/              # AI agent modules
│   │   │   ├── prompt_to_slide_agent.py
│   │   │   ├── text_generation_agent.py
│   │   │   ├── image_generation_agent.py
│   │   │   ├── diagram_generation_agent.py
│   │   │   ├── media_integration_agent.py
│   │   │   ├── stock_image_agent.py
│   │   │   ├── quiz_generation_agent.py
│   │   │   ├── speaker_notes_agent.py
│   │   │   ├── template_selection_agent.py
│   │   │   └── model_manager.py
│   │   ├── api/                 # FastAPI application
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── orchestrate.py
│   │   │       ├── slides.py
│   │   │       ├── notes.py
│   │   │       ├── quizzes.py
│   │   │       ├── export.py
│   │   │       └── generate.py
│   │   ├── exporters/           # Export modules
│   │   │   └── ppt_exporter.py
│   │   ├── utils/               # Utility functions
│   │   ├── config/              # Configuration files
│   │   │   └── model_registry.yaml
│   │   ├── config.py            # Configuration management
│   │   ├── ai_db.py             # Database connection
│   │   ├── init_db.py           # Database initialization
│   │   └── requirements.txt      # Python dependencies
│   └── .env                     # Environment variables
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ui/             # shadcn-ui components
│   │   │   ├── TopBar.tsx
│   │   │   ├── ProfileModal.tsx
│   │   │   ├── SettingsModal.tsx
│   │   │   └── ExportDialog.tsx
│   │   ├── pages/              # Page components
│   │   │   ├── Landing.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── Home.tsx
│   │   │   ├── Editor.tsx
│   │   │   └── NotFound.tsx
│   │   ├── contexts/           # React contexts
│   │   │   ├── AuthContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── hooks/              # Custom hooks
│   │   ├── lib/                # Utility libraries
│   │   └── App.tsx             # Main app component
│   ├── package.json
│   └── vite.config.ts
│
├── go/                          # Go authentication service
│   ├── internal/
│   │   ├── Auth/               # Authentication logic
│   │   ├── db/                 # Database handlers
│   │   ├── handlers/           # HTTP handlers
│   │   ├── routes/             # Route definitions
│   │   ├── server/             # Server setup
│   │   └── config/             # Configuration
│   └── main.go                 # Entry point
│
└── models/                      # AI model files
    └── stable-diffusion-3.5-medium/
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Go 1.25 or higher
- MongoDB (local or Atlas)
- Gemini API key
- Ollama (for local model inference - optional but recommended)
- LibreOffice (for PDF export with template preservation - optional)

### Python Backend Setup

#### Option 1: Docker (Recommended)

Navigate to the AI backend directory:

```bash
cd ai
```

Build the Docker image:

```bash
docker build -t ai-service .
```

Run the container:

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/out:/app/src/out" \
  ai-service
```

The API will be available at http://localhost:8000

See `ai/DOCKER_README.md` for detailed Docker instructions.

#### Option 2: Local Setup

Navigate to the AI backend directory:

```bash
cd ai/src
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create environment file in `ai/` directory (not in `ai/src/`):

```env
AI_MONGODB_URI=mongodb://localhost:27017
AI_DB_NAME=ai_db

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_ID=gemini-2.5-flash

STABILITY_API_KEY=your_stability_key_here

UNSPLASH_API_KEY=your_unsplash_key_here
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here

# Ollama Configuration (for local model inference)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b

LLM_PROVIDER=gemini
STOCK_IMAGE_PROVIDER=unsplash
IMAGE_SOURCE=stock
```

Initialize the database:

```bash
python init_db.py
```

**Setup Ollama (Recommended for Content Expansion)**

Install Ollama:
- **Windows**: Download from https://ollama.com/download/windows
- **macOS**: `brew install ollama` or download from website
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

Pull the Deepseek model:
```bash
ollama pull deepseek-r1:1.5b
```

Verify Ollama is running:
```bash
cd ai/src
python test_ollama_connection.py
```

See `ai/OLLAMA_SETUP.md` for detailed instructions.

**Setup LibreOffice (Optional - for PDF Export)**

- **Windows**: Download from https://www.libreoffice.org/download/
- **macOS**: `brew install --cask libreoffice`
- **Linux**: `sudo apt-get install libreoffice`

See `ai/PDF_EXPORT_SETUP.md` for detailed instructions.

Start the API server:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Go Service Setup

Navigate to the Go service directory:

```bash
cd go
```

Set environment variables:

```bash
export GOOGLE_CLIENT_ID=your_google_client_id
export GOOGLE_CLIENT_SECRET=your_google_secret
export GOTH_GOOGLE_CALLBACK=http://localhost:8080/auth/google/callback
export SESSION_KEY=your_session_key
```

Install dependencies:

```bash
go mod download
```

Run the service:

```bash
go run main.go
```

## API Endpoints

### Main Orchestration Endpoint

POST /orchestrate
- Generates complete presentation with slides, notes, quizzes, media, and PPT
- Accepts prompt, userId, locale, context, and generation options
- Returns deckId, quizIds, media status, and base64-encoded PPT file

### Slide Management

POST /slides
- Creates slides from prompt without additional features

GET /slides/{deck_id}
- Retrieves deck details by ID

POST /slides/{deck_id}/export
- Exports deck as PPTX or PDF file

GET /slides/{deck_id}/download
- Downloads previously exported deck file

### Speaker Notes

POST /slides/{deck_id}/speaker-notes
- Generates speaker notes PDF for a deck

GET /slides/{deck_id}/speaker-notes/download
- Downloads previously generated speaker notes PDF

### Quiz Generation

POST /slides/{deck_id}/quizzes
- Generates quiz for a deck
- Returns JSON or PDF based on query parameter

### Individual Generation Endpoints

POST /generate-text
- Generates text content using LLM only

POST /generate-image
- Generates image using AI models

POST /generate-diagram
- Generates diagram based on description

POST /generate-slides
- Generates slides with media integration

POST /generate-media/{deck_id}
- Adds media to existing deck

POST /generate-notes
- Generates standalone lesson notes from prompt

## Usage Examples

### Basic Presentation Generation

Create a presentation about photosynthesis for 10th grade:

```json
POST /orchestrate
{
  "prompt": "Create a presentation about Photosynthesis",
  "userId": "user123",
  "locale": "en",
  "context": {
    "grade_level": "10th",
    "subject": "biology"
  },
  "generate_images": true,
  "generate_diagrams": true,
  "estimated_slides": 10
}
```

### Multi-language Support

Generate presentation in Hindi:

```json
POST /orchestrate
{
  "prompt": "प्रकाश संश्लेषण के बारे में प्रस्तुति बनाएं",
  "userId": "user123",
  "locale": "hi",
  "context": {
    "grade_level": "10th",
    "subject": "biology"
  }
}
```

### Custom Quiz Generation

Generate quiz with specific number of questions:

```json
POST /slides/{deck_id}/quizzes
{
  "userId": "user123",
  "quiz_type": "comprehensive",
  "difficulty": null
}
```

Query parameter: ?download=pdf for PDF export

## Technologies Used

### Backend Technologies

**Python 3.8+**
- FastAPI for REST API
- Pymongo for MongoDB integration
- python-pptx for PowerPoint generation
- Pillow for image processing
- Transformers and Diffusers for AI models
- ReportLab for PDF generation (fallback)
- LibreOffice headless mode for PDF export (primary)
- Graphviz for diagram generation
- Matplotlib for data visualization

**AI Models and Services**
- **Google Gemini API** (Primary): Text generation, prompt analysis, slide structure
- **Ollama with Deepseek-R1:1.5b** (Local): Content expansion and keyword elaboration
- **HuggingFace API**: Fallback for text and image generation
- **Stability AI API**: High-quality image generation
- **Stable Diffusion** (Local): Local image generation option
- **Graphviz**: Flowcharts, process diagrams, hierarchies
- **Matplotlib**: Charts, graphs, data visualizations
- **BLIP Model**: Auto-captioning for generated images

Image Services
- Unsplash API
- Pexels API
- Pixabay API

### Frontend Technologies

React 18
- TypeScript for type safety
- Vite for build tooling
- React Router for navigation
- TanStack Query for data fetching
- Framer Motion for animations

UI Libraries
- shadcn-ui component library
- Tailwind CSS for styling
- Radix UI primitives
- Lucide React for icons

### Backend Services

Go 1.25
- Gin framework for HTTP server
- MongoDB driver for database
- OAuth2 for authentication
- Gorilla sessions for session management

### Database

MongoDB
- Document-based storage
- Text search capabilities
- Indexed collections for performance

## Configuration

### Model Configuration

Model settings are configured in `ai/src/config/model_registry.yaml`:

- Model selection and switching
- Generation parameters
- Quantization settings
- Device management

### Environment Variables

Required Variables:
- AI_MONGODB_URI: MongoDB connection string
- AI_DB_NAME: Database name
- GEMINI_API_KEY: Google Gemini API key

**Optional Variables:**
- STABILITY_API_KEY: For AI image generation via Stability AI
- UNSPLASH_API_KEY: For stock images from Unsplash
- PEXELS_API_KEY: For stock images from Pexels
- PIXABAY_API_KEY: For stock images from Pixabay
- HF_API_KEY: For HuggingFace API access
- OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
- OLLAMA_MODEL: Ollama model name (default: deepseek-r1:1.5b)
- LLM_PROVIDER: Model provider selection (gemini, huggingface, ollama)
- STOCK_IMAGE_PROVIDER: Preferred image service (unsplash, pexels, pixabay)
- IMAGE_SOURCE: Image source preference (stock, generate, or both)

### Frontend Configuration

API endpoint configuration in `frontend/src/lib/api.ts`:
- Base URL for backend API
- Request timeout settings
- Error handling configuration

## Development

### Running in Development Mode

Python Backend:
```bash
cd ai/src
uvicorn api.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

Go Service:
```bash
cd go
go run main.go
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

Go Service:
```bash
cd go
go build -o aieduthon-auth
```

### Database Migrations

Initialize database schema:
```bash
cd ai/src
python init_db.py
```

### Testing

API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features in Detail

### Content Personalization

The system analyzes prompts to determine:
- Subject matter and complexity
- Target audience level
- Appropriate content depth
- Language complexity
- Cultural context

### Media Intelligence

**Automatic Media Selection**
- Slide title and content analysis
- Semantic keyword extraction
- Context-aware image matching
- Diagram type detection (flowchart, hierarchy, cycle, chart)
- Visual coherence maintenance
- Multi-provider redundancy (Unsplash → Pexels → Pixabay fallback)

**Caching and Performance**
- Multi-level caching system (text and image generation)
- Session-based context tracking
- Lazy model loading for efficiency
- Database-backed cache persistence

### Export Capabilities

PowerPoint Export:
- Full slide deck with all content
- Integrated images and diagrams
- Proper formatting and layouts
- Template application
- Content validation
- **Database Storage**: PPT files are automatically stored in MongoDB for easy retrieval
- **Smart Slide Management**: Automatically removes unused template slides while preserving important conclusion slides
- **Adaptive Templates**: Works with templates of any size - removes middle slides when fewer slides are needed

**PDF Export:**
- Speaker notes as PDF (with template preservation via LibreOffice)
- Quiz documents as PDF
- Standalone lesson notes
- Professional formatting
- Template and design preservation (when using LibreOffice)
- Automatic fallback to ReportLab if LibreOffice unavailable

## Project Status

### ✅ Core Features: Fully Implemented

**Content Generation**
- ✅ Three-pass slide generation pipeline (Gemini → Gemini → Deepseek)
- ✅ Multi-language support (English, Hindi, Tamil)
- ✅ Audience adaptation (grade levels, complexity adjustment)
- ✅ Context-aware content personalization

**Media Integration**
- ✅ Stock image integration (Unsplash, Pexels, Pixabay)
- ✅ AI image generation (Stability AI, HuggingFace, Local SD)
- ✅ Diagram generation (Graphviz, Matplotlib)
- ✅ Multiple diagram types (flowchart, hierarchy, cycle, chart)
- ✅ Auto-captioning for generated images

**Additional Features**
- ✅ Speaker notes generation with PDF export
- ✅ Quiz generation (MCQ, True/False, Fill-in-blank)
- ✅ Multiple quiz types (comprehensive, per-topic, final-only)
- ✅ PowerPoint export (PPTX format)
- ✅ PDF export with template preservation (LibreOffice)
- ✅ Docker containerization for AI service
- ✅ PPT storage in database
- ✅ Smart template slide management
- ✅ Adaptive slide removal with conclusion slide preservation
- ✅ Multi-provider AI model support
- ✅ Local model inference via Ollama
- ✅ Caching system for performance
- ✅ Session tracking and context management

### ⚠️ Partial Features

- Presentation style variations (currently educational style - can be extended)
- Adaptive layout selection (currently random template selection - can be enhanced)

### 🔮 Future Enhancements

- Voice input for prompts
- Enhanced presentation style options
- Content-aware layout optimization
- Additional language support
- Real-time collaboration features
- Advanced analytics and insights

## Additional Documentation

For more detailed information, see:

- **API Endpoints**: `API_ENDPOINTS.md` - Complete API reference with examples
- **Docker Setup**: `ai/DOCKER_README.md` - Docker deployment guide
- **Ollama Setup**: `ai/OLLAMA_SETUP.md` - Local model inference setup
- **PDF Export**: `ai/PDF_EXPORT_SETUP.md` - LibreOffice PDF export guide
- **Stock Images**: `ai/src/STOCK_IMAGE_SETUP.md` - Stock image API configuration
- **Pipeline Status**: `ai/src/PIPELINE_STATUS.md` - Detailed pipeline architecture
- **Requirements Compliance**: `REQUIREMENTS_COMPLIANCE.md` - Feature compliance analysis
- **Quick Start**: `ai/src/QUICKSTART.md` - Quick setup guide

## License

This project is part of the AIEduthon educational platform.

## Support

For issues, questions, or contributions, please refer to the project documentation in the respective component directories.

## Contributing

Contributions are welcome! Please ensure you:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Test with multiple AI providers when possible
