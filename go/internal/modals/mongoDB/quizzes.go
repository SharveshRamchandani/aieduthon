package mongodb

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// Question represents a quiz question
type Question struct {
	QuestionText  string   `bson:"question_text" json:"question_text"`
	QuestionType  string   `bson:"question_type" json:"question_type"`
	Options       []string `bson:"options" json:"options"`
	CorrectAnswer string   `bson:"correct_answer" json:"correct_answer"`
	Explanation   string   `bson:"explanation" json:"explanation"`
	Difficulty    string   `bson:"difficulty" json:"difficulty"`
	Topic         string   `bson:"topic" json:"topic"`
}

// AccuracyStats represents quiz accuracy statistics
type AccuracyStats struct {
	TotalAttempts   int     `bson:"total_attempts" json:"total_attempts"`
	CorrectAttempts int     `bson:"correct_attempts" json:"correct_attempts"`
	AverageScore    float64 `bson:"average_score" json:"average_score"`
}

// QuizMetadata represents metadata for a quiz
type QuizMetadata struct {
	TotalQuestions  int       `bson:"total_questions" json:"total_questions"`
	EstimatedTime   int       `bson:"estimated_time" json:"estimated_time"`
	DifficultyLevel string    `bson:"difficulty_level" json:"difficulty_level"`
	TopicsCovered   []string  `bson:"topics_covered" json:"topics_covered"`
	GeneratedAt     time.Time `bson:"generated_at" json:"generated_at"`
	UserID          string    `bson:"user_id" json:"user_id"`
}

// Quiz represents generated quizzes for slides
type Quiz struct {
	ID               primitive.ObjectID     `bson:"_id,omitempty" json:"id"`
	SlideID          string                 `bson:"slideId" json:"slideId"`
	Title            string                 `bson:"title" json:"title"`
	Questions        []Question             `bson:"questions" json:"questions"`
	AccuracyStats    AccuracyStats          `bson:"accuracy_stats" json:"accuracy_stats"`
	LiveQuizExport   map[string]interface{} `bson:"live_quiz_export,omitempty" json:"live_quiz_export,omitempty"` // For Google Forms
	InjectedPosition string                 `bson:"injected_position" json:"injected_position"`                   // "after_section" | "final"
	Metadata         QuizMetadata           `bson:"metadata" json:"metadata"`
}
