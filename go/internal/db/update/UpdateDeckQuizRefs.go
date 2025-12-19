package update

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.uber.org/zap"
)

// UpdateDeckQuizRefs updates a deck with quiz references
func UpdateDeckQuizRefs(deckID string, quizRefs []string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for quiz refs update", zap.String("deck_id", deckID), zap.Error(err))
		return err
	}

	updateData := bson.M{
		"$set": bson.M{
			"quiz_refs": quizRefs,
		},
	}

	result, err := collection.UpdateOne(ctx, bson.M{"_id": objID}, updateData)
	if err != nil {
		logger.Log.Error("Failed to update deck with quiz refs",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return err
	}

	if result.MatchedCount == 0 {
		logger.Log.Warn("Deck not found for quiz refs update", zap.String("deck_id", deckID))
		return nil // Not an error, just no match
	}

	logger.Log.Debug("Successfully updated deck with quiz refs",
		zap.String("deck_id", deckID),
		zap.Int("quiz_count", len(quizRefs)))

	return nil
}
