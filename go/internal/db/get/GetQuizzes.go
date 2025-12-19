package get

import (
	"context"
	"time"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.uber.org/zap"
)

// GetQuizzesByDeckID retrieves all quizzes for a specific deck
func GetQuizzesByDeckID(deckID string) ([]mongodb.Quiz, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("quizzes")

	cursor, err := collection.Find(ctx, bson.M{"slideId": deckID})
	if err != nil {
		logger.Log.Error("Failed to query quizzes from database",
			zap.Error(err),
			zap.String("collection", collection.Name()),
			zap.String("deck_id", deckID))
		return nil, err
	}
	defer cursor.Close(ctx)

	var quizzes []mongodb.Quiz
	if err = cursor.All(ctx, &quizzes); err != nil {
		logger.Log.Error("Failed to decode quizzes",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return nil, err
	}

	logger.Log.Debug("Quizzes found", zap.String("deck_id", deckID), zap.Int("count", len(quizzes)))
	return quizzes, nil
}

// GetQuizByIds retrieves multiple quizzes by their IDs
func GetQuizByIds(quizIDs []string) ([]mongodb.Quiz, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("quizzes")

	// Convert string IDs to ObjectIDs
	objectIDs := make([]primitive.ObjectID, 0, len(quizIDs))
	for _, id := range quizIDs {
		objID, err := primitive.ObjectIDFromHex(id)
		if err != nil {
			logger.Log.Warn("Invalid quiz ID format, skipping", zap.String("quiz_id", id), zap.Error(err))
			continue
		}
		objectIDs = append(objectIDs, objID)
	}

	if len(objectIDs) == 0 {
		return []mongodb.Quiz{}, nil
	}

	cursor, err := collection.Find(ctx, bson.M{"_id": bson.M{"$in": objectIDs}})
	if err != nil {
		logger.Log.Error("Failed to query quizzes by IDs",
			zap.Error(err),
			zap.Int("count", len(quizIDs)))
		return nil, err
	}
	defer cursor.Close(ctx)

	var quizzes []mongodb.Quiz
	if err = cursor.All(ctx, &quizzes); err != nil {
		logger.Log.Error("Failed to decode quizzes",
			zap.Error(err))
		return nil, err
	}

	logger.Log.Debug("Quizzes found by IDs", zap.Int("requested", len(quizIDs)), zap.Int("found", len(quizzes)))
	return quizzes, nil
}
