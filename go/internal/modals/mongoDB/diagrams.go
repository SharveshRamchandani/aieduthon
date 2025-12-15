package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Diagram represents generated diagrams (flowcharts, charts, cycles, etc.)
type Diagram struct {
	ID          primitive.ObjectID  `bson:"_id,omitempty" json:"id"`
	SlideID     *primitive.ObjectID `bson:"slideId,omitempty" json:"slideId,omitempty"`
	DiagramType string              `bson:"diagram_type" json:"diagram_type"` // "flowchart" | "chart" | "cycle" | "generic"
	Description string              `bson:"description" json:"description"`
	FilePath    string              `bson:"file_path" json:"file_path"`
	Format      string              `bson:"format" json:"format"` // "png" | "svg" | "pdf"
	Tags        []string            `bson:"tags" json:"tags"`
	CreatedAt   time.Time           `bson:"created_at" json:"created_at"`
}
