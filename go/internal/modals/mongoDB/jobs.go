package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Job represents background jobs and their status
type Job struct {
	ID          primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	JobID       string                 `bson:"jobId" json:"jobId"` // UNIQUE
	ServiceType string                 `bson:"service_type" json:"service_type"`
	Status      string                 `bson:"status" json:"status"` // "pending" | "processing" | "completed" | "failed"
	Timestamp   time.Time              `bson:"timestamp" json:"timestamp"`
	Input       map[string]interface{} `bson:"input" json:"input"`
	Output      map[string]interface{} `bson:"output,omitempty" json:"output,omitempty"`
	Error       string                 `bson:"error,omitempty" json:"error,omitempty"`
	Metadata    map[string]interface{} `bson:"metadata,omitempty" json:"metadata,omitempty"`
}
