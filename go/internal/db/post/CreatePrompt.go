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

// CreatePrompt stores a new prompt in the database and returns its ID
func CreatePrompt(userID, promptText, locale string, promptContext map[string]interface{}) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("prompts")

	prompt := mongodb.Prompt{
		UserID:     userID,
		PromptText: promptText,
		Timestamp:  time.Now(),
		Locale:     locale,
		Context:    promptContext,
		Status:     "processed",
	}

	result, err := collection.InsertOne(ctx, prompt)
	if err != nil {
		logger.Log.Error("Failed to insert prompt into database",
			zap.Error(err),
			zap.String("user_id", userID),
			zap.String("locale", locale))
		return "", err
	}

	promptID := result.InsertedID.(primitive.ObjectID).Hex()
	logger.Log.Debug("Successfully created prompt",
		zap.String("prompt_id", promptID),
		zap.String("user_id", userID))

	return promptID, nil
}
