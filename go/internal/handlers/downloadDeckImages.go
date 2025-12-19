package handlers

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func DownloadDeckImages(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	logger.Log.Debug("Downloading deck images", zap.String("deck_id", deckId))

	// Verify deck exists in database first
	deckInfo, err := get.GetDeckForImages(deckId)
	if err != nil {
		logger.Log.Error("Failed to fetch deck from database", zap.Error(err), zap.String("deck_id", deckId))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if deckInfo == nil {
		logger.Log.Debug("Deck not found", zap.String("deck_id", deckId))
		c.JSON(http.StatusNotFound, gin.H{"error": "Deck not found"})
		return
	}

	// Call AI service to generate ZIP (AI handles file system access)
	downloadImagesURL := fmt.Sprintf("%s/slides/%s/images-zip", os.Getenv("AI_URL"), deckId)
	logger.Log.Debug("AI service URL", zap.String("url", downloadImagesURL))

	req, err := http.NewRequest("GET", downloadImagesURL, nil)
	if err != nil {
		logger.Log.Error("Failed to create request to AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		logger.Log.Error("Failed to receive data from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	defer res.Body.Close()

	// Read response body
	body, err := io.ReadAll(res.Body)
	if err != nil {
		logger.Log.Error("Failed to read response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Get filename from Content-Disposition header or use default
	filename := fmt.Sprintf("deck_%s_images.zip", deckId)
	contentDisposition := res.Header.Get("Content-Disposition")
	if contentDisposition != "" {
		// Extract filename from Content-Disposition header
		// Format: attachment; filename="deck_images.zip"
		start := len(`attachment; filename="`)
		if len(contentDisposition) > start {
			endIdx := len(contentDisposition) - 1
			if endIdx > start {
				filename = contentDisposition[start:endIdx]
			}
		}
	}

	logger.Log.Info("Downloading deck images", zap.String("filename", filename), zap.Int("size", len(body)))

	// Set headers and return binary data
	c.Header("Content-Type", "application/zip")
	c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
	c.Data(res.StatusCode, "application/zip", body)
}
