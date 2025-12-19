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

// UpdateDeckMediaRefs updates a deck with media and diagram references
func UpdateDeckMediaRefs(deckID string, mediaRefs, diagramRefs interface{}, mediaMetadata interface{}) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for media refs update", zap.String("deck_id", deckID), zap.Error(err))
		return err
	}

	updateData := bson.M{
		"$set": bson.M{
			"media_generated_at": time.Now(),
		},
	}

	if mediaRefs != nil {
		updateData["$set"].(bson.M)["media_refs"] = mediaRefs
	}
	if diagramRefs != nil {
		updateData["$set"].(bson.M)["diagram_refs"] = diagramRefs
	}
	if mediaMetadata != nil {
		updateData["$set"].(bson.M)["media_metadata"] = mediaMetadata
	}

	result, err := collection.UpdateOne(ctx, bson.M{"_id": objID}, updateData)
	if err != nil {
		logger.Log.Error("Failed to update deck with media refs",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return err
	}

	if result.MatchedCount == 0 {
		logger.Log.Warn("Deck not found for media refs update", zap.String("deck_id", deckID))
		return nil // Not an error, just no match
	}

	logger.Log.Debug("Successfully updated deck with media refs",
		zap.String("deck_id", deckID))

	return nil
}
