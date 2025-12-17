package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// PopularityStats represents template popularity statistics
type PopularityStats struct {
	UsageCount int     `bson:"usage_count" json:"usage_count"`
	Rating     float64 `bson:"rating" json:"rating"`
}

// Template represents presentation templates
type Template struct {
	ID                     primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	TemplateID             string             `bson:"templateId" json:"templateId"` // UNIQUE
	Name                   string             `bson:"name" json:"name"`
	Style                  string             `bson:"style" json:"style"`
	RecommendedForAudience string             `bson:"recommended_for_audience" json:"recommended_for_audience"`
	PopularityStats        PopularityStats    `bson:"popularity_stats" json:"popularity_stats"`
	CreatedAt              time.Time          `bson:"created_at" json:"created_at"`
}
