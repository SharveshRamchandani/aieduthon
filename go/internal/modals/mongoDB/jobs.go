package mongodb

import "time"

type Job struct {
    JobID       string    `bson:"_id,omitempty" json:"jobId"`
    ServiceType string    `bson:"serviceType" json:"serviceType"`
    Status      string    `bson:"status" json:"status"`
    ResultURL   string    `bson:"resultUrl" json:"resultUrl"`
    Error       string    `bson:"error,omitempty" json:"error"`
    CreatedAt   time.Time `bson:"createdAt" json:"createdAt"`
    CompletedAt time.Time `bson:"completedAt,omitempty" json:"completedAt"`
}