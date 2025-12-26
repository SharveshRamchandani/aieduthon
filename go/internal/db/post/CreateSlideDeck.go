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

// CreateSlideDeck stores a new slide deck in the database and returns its ID
func CreateSlideDeck(promptID, userID string, slideData map[string]interface{}) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := get.GetCollections("slides")

	// Build slide document from the provided data
	slide := mongodb.Slide{
		ID:       primitive.NewObjectID(),
		PromptID: promptID,
	}

	// Map fields from slideData to slide struct
	if title, ok := slideData["title"].(string); ok {
		slide.Title = title
	}
	if sections, ok := slideData["sections"].([]interface{}); ok {
		slide.Sections = make([]string, len(sections))
		for i, s := range sections {
			if str, ok := s.(string); ok {
				slide.Sections[i] = str
			}
		}
	}
	if bullets, ok := slideData["bullets"].([]interface{}); ok {
		slide.Bullets = make([][]string, len(bullets))
		for i, b := range bullets {
			if arr, ok := b.([]interface{}); ok {
				slide.Bullets[i] = make([]string, len(arr))
				for j, item := range arr {
					if str, ok := item.(string); ok {
						slide.Bullets[i][j] = str
					}
				}
			}
		}
	}
	if examples, ok := slideData["examples"].([]interface{}); ok {
		slide.Examples = make([][]string, len(examples))
		for i, e := range examples {
			if arr, ok := e.([]interface{}); ok {
				slide.Examples[i] = make([]string, len(arr))
				for j, item := range arr {
					if str, ok := item.(string); ok {
						slide.Examples[i][j] = str
					}
				}
			}
		}
	}
	if keyPoints, ok := slideData["key_points"].([]interface{}); ok {
		slide.KeyPoints = make([][]string, len(keyPoints))
		for i, kp := range keyPoints {
			if arr, ok := kp.([]interface{}); ok {
				slide.KeyPoints[i] = make([]string, len(arr))
				for j, item := range arr {
					if str, ok := item.(string); ok {
						slide.KeyPoints[i][j] = str
					}
				}
			}
		}
	}
	if templatePath, ok := slideData["template_path"].(string); ok {
		slide.TemplatePath = templatePath
	}
	if style, ok := slideData["style"].(string); ok {
		slide.Style = style
	}

	// Set metadata from slideData if available
	if metadata, ok := slideData["metadata"].(map[string]interface{}); ok {
		if totalSlides, ok := metadata["total_slides"].(float64); ok {
			slide.Metadata.TotalSlides = int(totalSlides)
		}
		if estDuration, ok := metadata["estimated_duration"].(float64); ok {
			slide.Metadata.EstimatedDuration = int(estDuration)
		}
		if diffLevel, ok := metadata["difficulty_level"].(string); ok {
			slide.Metadata.DifficultyLevel = diffLevel
		}
		if targetAudience, ok := metadata["target_audience"].(string); ok {
			slide.Metadata.TargetAudience = targetAudience
		}
		if context, ok := metadata["context"].(map[string]interface{}); ok {
			slide.Metadata.Context = context
		}
		slide.Metadata.GeneratedAt = time.Now()
		slide.Metadata.UserID = userID
	} else {
		// Set default metadata
		slide.Metadata = mongodb.SlideMetadata{
			GeneratedAt: time.Now(),
			UserID:      userID,
		}
	}

	result, err := collection.InsertOne(ctx, slide)
	if err != nil {
		logger.Log.Error("Failed to insert slide deck into database",
			zap.Error(err),
			zap.String("prompt_id", promptID),
			zap.String("user_id", userID))
		return "", err
	}

	deckID := result.InsertedID.(primitive.ObjectID).Hex()
	logger.Log.Debug("Successfully created slide deck",
		zap.String("deck_id", deckID),
		zap.String("prompt_id", promptID))

	return deckID, nil
}
