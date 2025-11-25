package mongodb

import "time"

type Prompt struct {
	ID          string    `bson:"_id,omitempty" json:"id"`                       
	PromptID    string    `bson:"promptId" json:"promptId" validate:"required"`   
	UserID      string    `bson:"userId" json:"userId" validate:"required"`
	PromptText  string    `bson:"promptText" json:"promptText" validate:"required"`
	Subject     string    `bson:"subject" json:"subject"`
	GradeLevel  string    `bson:"gradeLevel" json:"gradeLevel"`
	Timestamp   time.Time `bson:"timestamp" json:"timestamp"`
	Context     string    `bson:"context" json:"context"`
	Locale      string    `bson:"locale" json:"locale"`
}