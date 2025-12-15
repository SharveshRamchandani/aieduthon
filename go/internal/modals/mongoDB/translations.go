package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Translation represents translated versions of slide content
type Translation struct {
	ID                primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	SlideID           primitive.ObjectID     `bson:"slideId" json:"slideId"`
	LangCode          string                 `bson:"lang_code" json:"lang_code"`
	Locale            string                 `bson:"locale" json:"locale"`
	TranslatedContent map[string]interface{} `bson:"translated_content" json:"translated_content"`
	CreatedAt         time.Time              `bson:"created_at" json:"created_at"`
}
