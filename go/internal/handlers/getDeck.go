package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func GetDeck(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	logger.Log.Debug("Fetching deck", zap.String("deck_id", deckId))

	// Get deck from database
	deck, err := get.GetDeck(deckId)
	if err != nil {
		logger.Log.Error("Failed to fetch deck from database", zap.Error(err), zap.String("deck_id", deckId))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if deck == nil {
		logger.Log.Debug("Deck not found", zap.String("deck_id", deckId))
		c.JSON(http.StatusNotFound, gin.H{"error": "Deck not found"})
		return
	}

	// Convert to JSON response
	deckJSON, err := json.Marshal(deck)
	if err != nil {
		logger.Log.Error("Failed to marshal deck to JSON", zap.Error(err), zap.String("deck_id", deckId))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	logger.Log.Debug("Deck retrieved successfully", zap.String("deck_id", deckId))
	c.Data(http.StatusOK, "application/json", deckJSON)
}
