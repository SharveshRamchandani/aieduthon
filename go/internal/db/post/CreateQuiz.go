package post

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.uber.org/zap"
)

// CreateQuiz stores a new quiz in the database and returns its ID
func CreateQuiz(deckID string, quizData map[string]interface{}) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("quizzes")

	// Build quiz document from the provided data
	quiz := mongodb.Quiz{
		ID:      primitive.NewObjectID(),
		SlideID: deckID,
	}

	// Map fields from quizData
	if title, ok := quizData["title"].(string); ok {
		quiz.Title = title
	}
	if questions, ok := quizData["questions"].([]interface{}); ok {
		quiz.Questions = make([]mongodb.Question, 0, len(questions))
		for _, q := range questions {
			if qMap, ok := q.(map[string]interface{}); ok {
				question := mongodb.Question{}
				if text, ok := qMap["question_text"].(string); ok {
					question.QuestionText = text
				}
				if qType, ok := qMap["question_type"].(string); ok {
					question.QuestionType = qType
				}
				if options, ok := qMap["options"].([]interface{}); ok {
					question.Options = make([]string, len(options))
					for j, opt := range options {
						if str, ok := opt.(string); ok {
							question.Options[j] = str
						}
					}
				}
				if answer, ok := qMap["correct_answer"].(string); ok {
					question.CorrectAnswer = answer
				}
				if explanation, ok := qMap["explanation"].(string); ok {
					question.Explanation = explanation
				}
				if difficulty, ok := qMap["difficulty"].(string); ok {
					question.Difficulty = difficulty
				}
				if topic, ok := qMap["topic"].(string); ok {
					question.Topic = topic
				}
				quiz.Questions = append(quiz.Questions, question)
			}
		}
	}
	if injectedPos, ok := quizData["injected_position"].(string); ok {
		quiz.InjectedPosition = injectedPos
	} else {
		quiz.InjectedPosition = "final"
	}

	// Set metadata
	if metadata, ok := quizData["metadata"].(map[string]interface{}); ok {
		if totalQ, ok := metadata["total_questions"].(float64); ok {
			quiz.Metadata.TotalQuestions = int(totalQ)
		}
		if estTime, ok := metadata["estimated_time"].(float64); ok {
			quiz.Metadata.EstimatedTime = int(estTime)
		}
		if diffLevel, ok := metadata["difficulty_level"].(string); ok {
			quiz.Metadata.DifficultyLevel = diffLevel
		}
		if topics, ok := metadata["topics_covered"].([]interface{}); ok {
			quiz.Metadata.TopicsCovered = make([]string, len(topics))
			for i, t := range topics {
				if str, ok := t.(string); ok {
					quiz.Metadata.TopicsCovered[i] = str
				}
			}
		}
		if userID, ok := metadata["user_id"].(string); ok {
			quiz.Metadata.UserID = userID
		}
		quiz.Metadata.GeneratedAt = time.Now()
	}

	result, err := collection.InsertOne(ctx, quiz)
	if err != nil {
		logger.Log.Error("Failed to insert quiz into database",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return "", err
	}

	quizID := result.InsertedID.(primitive.ObjectID).Hex()
	logger.Log.Debug("Successfully created quiz",
		zap.String("quiz_id", quizID),
		zap.String("deck_id", deckID))

	return quizID, nil
}
