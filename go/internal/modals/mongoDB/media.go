package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// MediaMetadata represents metadata for AI-generated images
type MediaMetadata struct {
	Model  string `bson:"model" json:"model"`
	Prompt string `bson:"prompt" json:"prompt"`
	Width  int    `bson:"width" json:"width"`
	Height int    `bson:"height" json:"height"`
}

// Media represents images and media assets (AI-generated, stock images, diagrams)
// Supports both AI-generated images and stock images
type Media struct {
	ID               primitive.ObjectID  `bson:"_id,omitempty" json:"id"`
	URL              string              `bson:"url" json:"url"`
	AltText          string              `bson:"alt_text" json:"alt_text"`
	Source           string              `bson:"source" json:"source"` // "ai_generated" | "stock_image" | "internal"
	Type             string              `bson:"type" json:"type"`     // "image" | "diagram"
	LinkedSlideID    *primitive.ObjectID `bson:"linked_slideId,omitempty" json:"linked_slideId,omitempty"`
	Locale           string              `bson:"locale" json:"locale"`
	Tags             []string            `bson:"tags" json:"tags"`
	GeneratedByAI    bool                `bson:"generated_by_ai" json:"generated_by_ai"`
	GenerationPrompt string              `bson:"generation_prompt,omitempty" json:"generation_prompt,omitempty"`
	CreatedAt        time.Time           `bson:"created_at" json:"created_at"`
	SessionID        *primitive.ObjectID `bson:"session_id,omitempty" json:"session_id,omitempty"`
	Metadata         *MediaMetadata      `bson:"metadata,omitempty" json:"metadata,omitempty"`

	// Stock image specific fields
	Provider    string                 `bson:"provider,omitempty" json:"provider,omitempty"`
	ImageID     string                 `bson:"image_id,omitempty" json:"image_id,omitempty"`
	Thumbnail   string                 `bson:"thumbnail,omitempty" json:"thumbnail,omitempty"`
	FullURL     string                 `bson:"full_url,omitempty" json:"full_url,omitempty"`
	Description string                 `bson:"description,omitempty" json:"description,omitempty"`
	Author      string                 `bson:"author,omitempty" json:"author,omitempty"`
	AuthorURL   string                 `bson:"author_url,omitempty" json:"author_url,omitempty"`
	SlideTitle  string                 `bson:"slide_title,omitempty" json:"slide_title,omitempty"`
	Query       string                 `bson:"query,omitempty" json:"query,omitempty"`
	Marker      map[string]interface{} `bson:"marker,omitempty" json:"marker,omitempty"`
	Width       *int                   `bson:"width,omitempty" json:"width,omitempty"`
	Height      *int                   `bson:"height,omitempty" json:"height,omitempty"`
}
