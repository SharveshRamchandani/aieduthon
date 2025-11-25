package mongodb

import "time"

type Template struct {
    TemplateID      string    `bson:"_id,omitempty" json:"templateId"`
    Name            string    `bson:"name" json:"name"`
    Style           string    `bson:"style" json:"style"`
    RecommendedFor  string    `bson:"recommendedFor" json:"recommendedFor"`
    PopularityScore int       `bson:"popularityScore" json:"popularityScore"`
    CreatedAt       time.Time `bson:"createdAt" json:"createdAt"`
}