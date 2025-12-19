package get

import (
	"context"
	"time"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.uber.org/zap"
)

// GetDeck retrieves a complete deck by ID
func GetDeck(deckID string) (*mongodb.Slide, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format", zap.String("deck_id", deckID), zap.Error(err))
		return nil, err
	}

	var deck mongodb.Slide
	err = collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&deck)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			logger.Log.Debug("Deck not found", zap.String("deck_id", deckID))
			return nil, nil
		}
		logger.Log.Error("Failed to query deck from database",
			zap.Error(err),
			zap.String("collection", collection.Name()),
			zap.String("deck_id", deckID))
		return nil, err
	}

	logger.Log.Debug("Deck found in database", zap.String("deck_id", deckID))
	return &deck, nil
}

// GetDeckForExport retrieves deck with PPT file data for export
func GetDeckForExport(deckID string) (map[string]interface{}, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for export", zap.String("deck_id", deckID), zap.Error(err))
		return nil, err
	}

	var result map[string]interface{}
	err = collection.FindOne(ctx, bson.M{"_id": objID}, options.FindOne().SetProjection(bson.M{
		"ppt_file":     1,
		"ppt_filename": 1,
		"_id":          1,
	})).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			logger.Log.Debug("Deck not found for export", zap.String("deck_id", deckID))
			return nil, nil
		}
		logger.Log.Error("Failed to query deck for export",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return nil, err
	}

	return result, nil
}

// GetDeckForImages retrieves deck with media and diagram references
func GetDeckForImages(deckID string) (map[string]interface{}, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for images", zap.String("deck_id", deckID), zap.Error(err))
		return nil, err
	}

	var result map[string]interface{}
	err = collection.FindOne(ctx, bson.M{"_id": objID}, options.FindOne().SetProjection(bson.M{
		"title":        1,
		"media_refs":   1,
		"diagram_refs": 1,
		"_id":          1,
	})).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			logger.Log.Debug("Deck not found for images", zap.String("deck_id", deckID))
			return nil, nil
		}
		logger.Log.Error("Failed to query deck for images",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return nil, err
	}

	return result, nil
}

// GetDeckTitle retrieves only the title of a deck
func GetDeckTitle(deckID string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("slides")

	objID, err := primitive.ObjectIDFromHex(deckID)
	if err != nil {
		logger.Log.Error("Invalid deck ID format for title", zap.String("deck_id", deckID), zap.Error(err))
		return "", err
	}

	var result struct {
		Title string `bson:"title"`
	}
	err = collection.FindOne(ctx, bson.M{"_id": objID}, options.FindOne().SetProjection(bson.M{
		"title": 1,
	})).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			logger.Log.Debug("Deck not found for title", zap.String("deck_id", deckID))
			return "", nil
		}
		logger.Log.Error("Failed to query deck title",
			zap.Error(err),
			zap.String("deck_id", deckID))
		return "", err
	}

	return result.Title, nil
}
