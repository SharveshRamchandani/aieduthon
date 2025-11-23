package mongodb

import "time"

type Media struct {
    MediaID      string    `bson:"_id,omitempty" json:"mediaId"`
    URL          string    `bson:"url" json:"url"`
    AltText      string    `bson:"altText" json:"altText"`
    Source       string    `bson:"source" json:"source"`
    Type         string    `bson:"type" json:"type"` // image, video, diagram
    LinkedSlide  string    `bson:"linkedSlideId" json:"linkedSlideId"`
    Tags         []string  `bson:"tags" json:"tags"`
    GeneratedByAI bool     `bson:"generatedByAI" json:"generatedByAI"`
    UploadedBy   string    `bson:"uploadedBy" json:"uploadedBy"`
    CreatedAt    time.Time `bson:"createdAt" json:"createdAt"`
}
