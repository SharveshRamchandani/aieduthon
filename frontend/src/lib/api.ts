/**
 * API Service for Multimodal AI Pipeline
 */

const API_BASE_URL = 'http://localhost:8000';

export interface GenerateTextRequest {
  prompt: string;
  context?: Record<string, any>;
  max_length?: number;
  temperature?: number;
  use_cache?: boolean;
}

export interface GenerateTextResponse {
  success: boolean;
  text: string;
  cached: boolean;
  model?: string;
}

export interface GenerateImageRequest {
  prompt: string;
  width?: number;
  height?: number;
  negative_prompt?: string;
  num_images?: number;
  use_cache?: boolean;
}

export interface GenerateImageResponse {
  success: boolean;
  urls: string[];
  cached: boolean;
  model?: string;
}

export interface GenerateDiagramRequest {
  diagram_type: string;
  description: string;
  data?: Record<string, any>;
  format?: string;
  style?: string;
}

export interface GenerateDiagramResponse {
  success: boolean;
  file_path: string;
  diagram_id?: string;
  type?: string;
}

export interface OrchestrateRequest {
  prompt: string;
  userId: string;
  locale?: string;
  context?: Record<string, any>;
  quiz_type?: string;
  audience_level?: string;
  presentation_style?: string;
  generate_images?: boolean;
  generate_diagrams?: boolean;
}

export interface OrchestrateResponse {
  deckId: string;
  promptId?: string;
  quizIds?: string[];
  mediaGenerated?: boolean;
  message?: string;
}

export interface SlideDeck {
  _id: string;
  title: string;
  sections: string[];
  bullets: string[][];
  examples?: string[][];
  key_points?: string[][];
  media_refs?: string[][];
  diagram_refs?: string[][];
  speaker_notes?: any[];
  metadata?: {
    total_slides: number;
    estimated_duration: number;
    difficulty_level: string;
    target_audience: string;
  };
}

// Text Generation
export async function generateText(request: GenerateTextRequest): Promise<GenerateTextResponse> {
  const response = await fetch(`${API_BASE_URL}/generate-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate text');
  }

  return response.json();
}

// Image Generation
export async function generateImage(request: GenerateImageRequest): Promise<GenerateImageResponse> {
  const response = await fetch(`${API_BASE_URL}/generate-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate image');
  }

  return response.json();
}

// Diagram Generation
export async function generateDiagram(request: GenerateDiagramRequest): Promise<GenerateDiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/generate-diagram`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate diagram');
  }

  return response.json();
}

// Orchestrate (Complete Presentation Generation)
export async function orchestrate(request: OrchestrateRequest): Promise<OrchestrateResponse> {
  const response = await fetch(`${API_BASE_URL}/orchestrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...request,
      locale: request.locale || 'en',
      quiz_type: request.quiz_type || 'comprehensive',
      presentation_style: request.presentation_style || 'educational',
      generate_images: request.generate_images ?? true,
      generate_diagrams: request.generate_diagrams ?? true,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to orchestrate presentation generation');
  }

  return response.json();
}

// Get Slide Deck
export async function getDeck(deckId: string): Promise<SlideDeck> {
  const response = await fetch(`${API_BASE_URL}/slides/${deckId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to fetch deck');
  }

  return response.json();
}

// Generate Media for Deck
export async function generateMediaForDeck(
  deckId: string,
  generateImages: boolean = true,
  generateDiagrams: boolean = true
): Promise<{ success: boolean; media_refs: string[][]; diagram_refs: string[][] }> {
  const response = await fetch(`${API_BASE_URL}/generate-media/${deckId}?generate_images=${generateImages}&generate_diagrams=${generateDiagrams}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate media');
  }

  return response.json();
}

// Export Deck to PPTX
export async function exportDeck(deckId: string, outputDir?: string): Promise<{ filePath: string }> {
  const response = await fetch(`${API_BASE_URL}/slides/${deckId}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ output_dir: outputDir }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to export deck');
  }

  return response.json();
}

// Generate Speaker Notes
export async function generateSpeakerNotes(
  deckId: string,
  userId: string,
  audienceLevel?: string,
  presentationStyle?: string
): Promise<{ success: boolean; speaker_notes: any[] }> {
  const response = await fetch(`${API_BASE_URL}/slides/${deckId}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId,
      audience_level: audienceLevel,
      presentation_style: presentationStyle || 'educational',
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate speaker notes');
  }

  return response.json();
}

// Generate Quiz
export async function generateQuiz(
  deckId: string,
  userId: string,
  quizType?: string,
  difficulty?: string
): Promise<{ success: boolean; quiz_ids: string[] }> {
  const response = await fetch(`${API_BASE_URL}/slides/${deckId}/quizzes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId,
      quiz_type: quizType || 'comprehensive',
      difficulty,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to generate quiz');
  }

  return response.json();
}

