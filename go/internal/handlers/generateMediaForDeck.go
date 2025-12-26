package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func GenerateMediaForDeck(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	// Get query parameters with defaults
	generateImages := true
	generateDiagrams := true

	if imgParam := c.Query("generate_images"); imgParam != "" {
		if val, err := strconv.ParseBool(imgParam); err == nil {
			generateImages = val
		}
	}

	if diagParam := c.Query("generate_diagrams"); diagParam != "" {
		if val, err := strconv.ParseBool(diagParam); err == nil {
			generateDiagrams = val
		}
	}

	logger.Log.Debug("Generating media for deck",
		zap.String("deck_id", deckId),
		zap.Bool("generate_images", generateImages),
		zap.Bool("generate_diagrams", generateDiagrams))

	// Call AI service
	generateMediaURL := fmt.Sprintf("%s/generate-media/%s?generate_images=%t&generate_diagrams=%t",
		os.Getenv("AI_URL"), deckId, generateImages, generateDiagrams)
	logger.Log.Debug("AI service URL", zap.String("url", generateMediaURL))

	req, err := http.NewRequest("POST", generateMediaURL, nil)
	if err != nil {
		logger.Log.Error("Failed to create request to AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		logger.Log.Error("Failed to receive data from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer res.Body.Close()

	// Read the response body
	var responseBody map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&responseBody); err != nil {
		logger.Log.Error("Failed to decode response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	logger.Log.Info("Response data", zap.Any("Data", responseBody))

	// Return the response with the same status code
	c.JSON(res.StatusCode, responseBody)
}
