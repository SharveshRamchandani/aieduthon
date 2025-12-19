package update

import (
	"context"
	"encoding/base64"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.uber.org/zap"
)

// UpdateDeckPPT updates a deck with PPT file data (base64 encoded)
func UpdateDeckPPT(deckID string, pptBytes []byte, filename string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for PPT update", zap.String("deck_id", deckID), zap.Error(err))
		return err
	}

	// Encode PPT bytes to base64
	pptBase64 := base64.StdEncoding.EncodeToString(pptBytes)

	updateData := bson.M{
		"$set": bson.M{
			"ppt_file":         pptBase64,
			"ppt_filename":     filename,
			"ppt_generated_at": time.Now(),
			"ppt_size_bytes":   len(pptBytes),
		},
	}

	result, err := collection.UpdateOne(ctx, bson.M{"_id": objID}, updateData)
	if err != nil {
		logger.Log.Error("Failed to update deck with PPT file",
			zap.Error(err),
			zap.String("deck_id", deckID),
			zap.String("filename", filename))
		return err
	}

	if result.MatchedCount == 0 {
		logger.Log.Warn("Deck not found for PPT update", zap.String("deck_id", deckID))
		return nil // Not an error, just no match
	}

	logger.Log.Debug("Successfully updated deck with PPT file",
		zap.String("deck_id", deckID),
		zap.String("filename", filename),
		zap.Int64("size_bytes", int64(len(pptBytes))))

	return nil
}
