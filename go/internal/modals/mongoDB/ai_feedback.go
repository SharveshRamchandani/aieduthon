package mongodb

import "time"

// AIFeedback represents user feedback on AI-generated content for model improvement
type AIFeedback struct {
	ID            string    `bson:"_id,omitempty" json:"id"`
	Prompt        string    `bson:"prompt" json:"prompt"`
	GeneratedText string    `bson:"generated_text" json:"generated_text"`
	Rating        int       `bson:"rating" json:"rating"` // 1-5
	Feedback      string    `bson:"feedback,omitempty" json:"feedback,omitempty"`
	UserID        string    `bson:"user_id,omitempty" json:"user_id,omitempty"`
	Model         string    `bson:"model" json:"model"`
	CreatedAt     time.Time `bson:"created_at" json:"created_at"`
}
