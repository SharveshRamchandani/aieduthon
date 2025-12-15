# AIEduthon - AI-Powered Educational Presentation Generator

Overview

AIEduthon is a comprehensive multimodal AI system that automatically generates educational presentations from text prompts. The platform creates complete slide decks with personalized content, relevant images, diagrams, speaker notes, and quizzes tailored to different educational levels and audiences.

The system uses advanced AI models to understand teacher prompts, generate structured content, integrate multimedia elements, and export professional PowerPoint presentations. It supports multiple languages, various educational levels, and customizable presentation styles.

Architecture

The application consists of three main components:

### Backend Services

Python FastAPI Service (Port 8000)
- Handles AI-powered content generation
- Manages slide deck creation and export
- Provides RESTful API endpoints
- Integrates with multiple AI models and image services

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

Key Features

### Content Generation

Personalized Slide Creation
- Converts text prompts into structured slide decks
- Analyzes subject matter and complexity automatically
- Generates appropriate number of slides based on content
- Creates logical sections and organization

Audience Adaptation
- Adjusts content for different grade levels
- Supports school, college, training, and professional audiences
- Modifies language complexity and tone
- Provides age-appropriate examples

Multi-language Support
- English (en)
- Hindi (hi)
- Tamil (ta)
- Culturally relevant content generation

### Media Integration

Stock Image Integration
- Automatically fetches relevant images from Unsplash, Pexels, and Pixabay
- Semantic search based on slide content
- Context-aware image selection
- Multiple image providers for redundancy

AI Image Generation
- Generates custom educational images using Stable Diffusion
- Creates context-specific illustrations
- Supports various image styles and formats

Diagram Generation
- Automatically creates flowcharts, process diagrams, and visualizations
- Uses Graphviz and Matplotlib for diagram creation
- Generates educational diagrams based on content type
- Supports multiple diagram formats

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

PowerPoint Export
- Exports complete presentations as PPTX files
- Integrates images and diagrams into slides
- Maintains proper formatting and layout
- Validates content quality

Project Structure

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

Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Go 1.25 or higher
- MongoDB (local or Atlas)
- Gemini API key

### Python Backend Setup

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

LLM_PROVIDER=gemini
STOCK_IMAGE_PROVIDER=unsplash
IMAGE_SOURCE=stock
```

Initialize the database:

```bash
python init_db.py
```

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

API Endpoints

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

Usage Examples

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

Technologies Used

### Backend Technologies

Python 3.8+
- FastAPI for REST API
- Pymongo for MongoDB integration
- python-pptx for PowerPoint generation
- Pillow for image processing
- Transformers and Diffusers for AI models
- ReportLab for PDF generation

AI Models and Services
- Google Gemini API for text generation
- Stable Diffusion for image generation
- Hugging Face Transformers for local models
- Graphviz and Matplotlib for diagrams

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

Configuration

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

Optional Variables:
- STABILITY_API_KEY: For AI image generation
- UNSPLASH_API_KEY: For stock images
- PEXELS_API_KEY: For stock images
- PIXABAY_API_KEY: For stock images
- LLM_PROVIDER: Model provider selection
- STOCK_IMAGE_PROVIDER: Preferred image service
- IMAGE_SOURCE: stock or generate

### Frontend Configuration

API endpoint configuration in `frontend/src/lib/api.ts`:
- Base URL for backend API
- Request timeout settings
- Error handling configuration

Development

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

Features in Detail

### Content Personalization

The system analyzes prompts to determine:
- Subject matter and complexity
- Target audience level
- Appropriate content depth
- Language complexity
- Cultural context

### Media Intelligence

Automatic media selection based on:
- Slide title and content analysis
- Semantic keyword extraction
- Context-aware image matching
- Diagram type detection
- Visual coherence maintenance

### Export Capabilities

PowerPoint Export:
- Full slide deck with all content
- Integrated images and diagrams
- Proper formatting and layouts
- Template application
- Content validation

PDF Export:
- Speaker notes as PDF
- Quiz documents as PDF
- Standalone lesson notes
- Professional formatting

Project Status

Core Features: Fully Implemented
- Slide generation from prompts
- Multi-language support
- Image and diagram integration
- Speaker notes generation
- Quiz generation
- PowerPoint export

Partial Features:
- Presentation style variations (currently educational style)
- Adaptive layout selection (currently random template selection)

Future Enhancements:
- Voice input for prompts
- Enhanced presentation style options
- Content-aware layout optimization
- Additional language support

License

This project is part of the AIEduthon educational platform.
Support

For issues, questions, or contributions, please refer to the project documentation in the respective component directories.
