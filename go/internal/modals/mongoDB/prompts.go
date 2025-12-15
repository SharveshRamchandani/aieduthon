package mongodb

import "time"

type Prompt struct {
	ID         string                 `bson:"_id,omitempty" json:"id"`
	UserID     string                 `bson:"userId" json:"userId" validate:"required"`
	PromptText string                 `bson:"prompt_text" json:"prompt_text" validate:"required"`
	Timestamp  time.Time              `bson:"timestamp" json:"timestamp"`
	Locale     string                 `bson:"locale" json:"locale"`
	Context    map[string]interface{} `bson:"context,omitempty" json:"context,omitempty"`
	Status     string                 `bson:"status" json:"status"` // default: "processed"
}
