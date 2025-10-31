package mongodb

import "time"

type Analytics struct {
    AnalyticsID    string                 `bson:"_id,omitempty" json:"analyticsId"`
    UserID         string                 `bson:"userId" json:"userId"`
    Timestamp      time.Time              `bson:"timestamp" json:"timestamp"`
    DeckID         string                 `bson:"deckId" json:"deckId"`
    TopicsGenerated int                    `bson:"topicsGenerated" json:"topicsGenerated"`
    TimeSaved      float64                `bson:"timeSaved" json:"timeSaved"`
    QuizAccuracy   float64                `bson:"quizAccuracy" json:"quizAccuracy"`
    TemplateUsed   string                 `bson:"templateUsed" json:"templateUsed"`
    UsageMetrics   map[string]interface{} `bson:"usageMetrics" json:"usageMetrics"`
}