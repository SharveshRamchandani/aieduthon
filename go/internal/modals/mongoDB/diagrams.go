package mongodb

import "time"

type Diagram struct {
    DiagramID     string    `bson:"_id,omitempty" json:"diagramId"`
    SlideID       string    `bson:"slideId" json:"slideId"`
    DiagramSpec   string    `bson:"diagramSpec" json:"diagramSpec"` // could be JSON or text
    ImageURL      string    `bson:"imageUrl" json:"imageUrl"`
    DiagramType   string    `bson:"diagramType" json:"diagramType"`
    GeneratedByAI bool      `bson:"generatedByAI" json:"generatedByAI"`
    Tags          []string  `bson:"tags" json:"tags"`
    CreatedAt     time.Time `bson:"createdAt" json:"createdAt"`
}