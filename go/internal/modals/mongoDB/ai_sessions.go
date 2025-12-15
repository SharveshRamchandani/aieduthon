package mongodb

import "time"

// AISession represents AI generation sessions for auditing and analytics
type AISession struct {
	ID        string                 `bson:"_id,omitempty" json:"id"`
	Prompt    string                 `bson:"prompt" json:"prompt"`
	Context   map[string]interface{} `bson:"context" json:"context"`
	Model     string                 `bson:"model" json:"model"`
	Status    string                 `bson:"status" json:"status"` // "processing", "completed", "failed"
	Success   bool                   `bson:"success" json:"success"`
	CreatedAt time.Time              `bson:"created_at" json:"created_at"`
	UpdatedAt time.Time              `bson:"updated_at" json:"updated_at"`
	Metadata  map[string]interface{} `bson:"metadata,omitempty" json:"metadata,omitempty"`
}
