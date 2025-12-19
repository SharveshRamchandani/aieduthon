package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	interaction "github.com/SharveshRamchandani/aieduthon.git/internal/modals/Interaction"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func GenerateSpeakerNotes(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	var input interaction.GenerateSpeakerNotes

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to receive input for generating speaker notes", zap.Error(err))
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Get user ID from JWT claims if not provided in request
	if input.UserId == "" {
		claims, exists := c.Get("claims")
		if exists {
			claimsMap, ok := claims.(map[string]any)
			if ok {
				if id, ok := claimsMap["ID"].(string); ok && id != "" {
					input.UserId = id
				} else if email, ok := claimsMap["email"].(string); ok && email != "" {
					input.UserId = email
				}
			}
		}
	}

	// If still no userId, return error
	if input.UserId == "" {
		logger.Log.Error("User ID not found in request or JWT claims")
		c.JSON(http.StatusBadRequest, gin.H{"error": "User ID is required"})
		return
	}

	// Set defaults
	if input.PresentationStyle == "" {
		input.PresentationStyle = "educational"
	}

	logger.Log.Debug("Generating speaker notes",
		zap.String("deck_id", deckId),
		zap.String("user_id", input.UserId),
		zap.String("presentation_style", input.PresentationStyle))

	// Get deck title from database for PDF filename
	deckTitle, err := get.GetDeckTitle(deckId)
	if err != nil {
		logger.Log.Warn("Failed to get deck title from database, using default", zap.Error(err), zap.String("deck_id", deckId))
		deckTitle = "Presentation"
	}
	if deckTitle == "" {
		deckTitle = "Presentation"
	}

	// Create request payload
	requestPayload := map[string]interface{}{
		"userId":             input.UserId,
		"presentation_style": input.PresentationStyle,
	}
	if input.AudienceLevel != "" {
		requestPayload["audience_level"] = input.AudienceLevel
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("Failed to parse struct to json", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Call AI service
	speakerNotesURL := fmt.Sprintf("%s/slides/%s/speaker-notes", os.Getenv("AI_URL"), deckId)
	logger.Log.Debug("AI service URL", zap.String("url", speakerNotesURL))

	req, err := http.NewRequest("POST", speakerNotesURL, bytes.NewBuffer(jsonData))
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

	// Read response body (PDF file)
	body, err := io.ReadAll(res.Body)
	if err != nil {
		logger.Log.Error("Failed to read response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Get filename from Content-Disposition header or use default
	filename := fmt.Sprintf("speaker_notes_%s.pdf", deckId)
	contentDisposition := res.Header.Get("Content-Disposition")
	if contentDisposition != "" {
		// Extract filename from Content-Disposition header
		start := len(`attachment; filename="`)
		if len(contentDisposition) > start {
			endIdx := len(contentDisposition) - 1
			if endIdx > start {
				filename = contentDisposition[start:endIdx]
			}
		}
	}

	logger.Log.Info("Generating speaker notes", zap.String("filename", filename), zap.Int("size", len(body)))

	// Set headers and return PDF binary data
	c.Header("Content-Type", "application/pdf")
	c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
	c.Data(res.StatusCode, "application/pdf", body)
}
