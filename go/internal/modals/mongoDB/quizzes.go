package mongodb

import "time"

type Question struct {
    Type    string   `bson:"type" json:"type"`
    Text    string   `bson:"text" json:"text"`
    Options []string `bson:"options" json:"options"`
    Answer  string   `bson:"answer" json:"answer"`
}

type Quiz struct {
    QuizID        string      `bson:"_id,omitempty" json:"quizId"`
    SlideID       string      `bson:"slideId" json:"slideId"`
    Questions     []Question  `bson:"questions" json:"questions"`
    AccuracyStats float64     `bson:"accuracyStats" json:"accuracyStats"`
    LiveQuizLink  string      `bson:"liveQuizLink" json:"liveQuizLink"`
    Position      int         `bson:"position" json:"position"`
    CreatedAt     time.Time   `bson:"createdAt" json:"createdAt"`
}