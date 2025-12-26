package update

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.uber.org/zap"
)

// UpdateDeckSpeakerNotes updates a deck with speaker notes
func UpdateDeckSpeakerNotes(deckID string, speakerNotes []mongodb.SpeakerNote) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for speaker notes update", zap.String("deck_id", deckID), zap.Error(err))
		return err
	}

	updateData := bson.M{
		"$set": bson.M{
			"speaker_notes": speakerNotes,
		},
	}

	result, err := collection.UpdateOne(ctx, bson.M{"_id": objID}, updateData)
	if err != nil {
		logger.Log.Error("Failed to update deck with speaker notes",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return err
	}

	if result.MatchedCount == 0 {
		logger.Log.Warn("Deck not found for speaker notes update", zap.String("deck_id", deckID))
		return nil // Not an error, just no match
	}

	logger.Log.Debug("Successfully updated deck with speaker notes",
		zap.String("deck_id", deckID),
		zap.Int("notes_count", len(speakerNotes)))

	return nil
}
