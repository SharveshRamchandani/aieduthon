package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Analytics represents analytics events for tracking usage
type Analytics struct {
	ID           primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	UserID       string                 `bson:"userId" json:"userId"`
	Timestamp    time.Time              `bson:"timestamp" json:"timestamp"`
	DeckID       string                 `bson:"deckId" json:"deckId"`
	EventType    string                 `bson:"event_type" json:"event_type"` // "slide_generated", "quiz_generated", "notes_generated", "media_integrated"
	Data         map[string]interface{} `bson:"data" json:"data"`
	Service      string                 `bson:"service" json:"service"`
	TemplateUsed string                 `bson:"template_used,omitempty" json:"template_used,omitempty"`
}
