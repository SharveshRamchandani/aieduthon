package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// AIOutput represents AI generation outputs for auditing and analytics
// Can represent both text and image outputs
type AIOutput struct {
	ID            primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	SessionID     *primitive.ObjectID    `bson:"session_id,omitempty" json:"session_id,omitempty"`
	Type          string                 `bson:"type,omitempty" json:"type,omitempty"` // "image" for image outputs, empty for text
	Prompt        string                 `bson:"prompt" json:"prompt"`
	GeneratedText string                 `bson:"generated_text,omitempty" json:"generated_text,omitempty"` // For text outputs
	FilePath      string                 `bson:"file_path,omitempty" json:"file_path,omitempty"`           // For image outputs
	Metadata      map[string]interface{} `bson:"metadata" json:"metadata"`
	Model         string                 `bson:"model" json:"model"`
	CreatedAt     time.Time              `bson:"created_at" json:"created_at"`
}
