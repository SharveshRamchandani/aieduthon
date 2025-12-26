package handlers

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db/update"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	interaction "github.com/SharveshRamchandani/aieduthon.git/internal/modals/Interaction"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func ExportDeck(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	var input interaction.ExportDeck

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to receive input for exporting deck", zap.Error(err))
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Set defaults
	if input.Format == "" {
		input.Format = "pptx"
	}
	if input.UserName == "" {
		input.UserName = "user"
	}

	logger.Log.Debug("Exporting deck",
		zap.String("deck_id", deckId),
		zap.String("format", input.Format),
		zap.String("user_name", input.UserName))

	// Check if PPTX already exists in DB (only for PPTX format)
	if input.Format == "pptx" {
		deckData, err := get.GetDeckForExport(deckId)
		if err != nil {
			logger.Log.Error("Failed to check deck in database", zap.Error(err), zap.String("deck_id", deckId))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		if deckData != nil {
			if pptFile, ok := deckData["ppt_file"].(string); ok && pptFile != "" {
				// Decode base64 PPT file
				pptBytes, err := base64.StdEncoding.DecodeString(pptFile)
				if err != nil {
					logger.Log.Warn("Failed to decode PPT from DB, will regenerate", zap.Error(err), zap.String("deck_id", deckId))
				} else {
					filename := "deck_" + deckId + ".pptx"
					if pptFilename, ok := deckData["ppt_filename"].(string); ok && pptFilename != "" {
						filename = pptFilename
					}

					logger.Log.Debug("Serving PPT from database", zap.String("deck_id", deckId), zap.String("filename", filename))
					c.Header("Content-Type", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
					c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
					c.Data(http.StatusOK, "application/vnd.openxmlformats-officedocument.presentationml.presentation", pptBytes)
					return
				}
			}
		}
	}

	// Create request payload
	requestPayload := map[string]interface{}{
		"format":    input.Format,
		"user_name": input.UserName,
	}
	if input.OutputDir != nil {
		requestPayload["output_dir"] = *input.OutputDir
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("Failed to parse struct to json", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Call AI service to generate export
	exportURL := fmt.Sprintf("%s/slides/%s/export", os.Getenv("AI_URL"), deckId)
	logger.Log.Debug("AI service URL", zap.String("url", exportURL))

	req, err := http.NewRequest("POST", exportURL, bytes.NewBuffer(jsonData))
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

	// Read response body (binary file)
	body, err := io.ReadAll(res.Body)
	if err != nil {
		logger.Log.Error("Failed to read response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Get filename from Content-Disposition header or use default
	filename := fmt.Sprintf("deck_%s.%s", deckId, input.Format)
	contentDisposition := res.Header.Get("Content-Disposition")
	if contentDisposition != "" {
		// Extract filename from Content-Disposition header
		// Format: attachment; filename="deck.pptx"
		start := len(`attachment; filename="`)
		if len(contentDisposition) > start {
			endIdx := len(contentDisposition) - 1
			if endIdx > start {
				filename = contentDisposition[start:endIdx]
			}
		}
	}

	// Determine media type based on format
	mediaType := "application/vnd.openxmlformats-officedocument.presentationml.presentation"
	if input.Format == "pdf" {
		mediaType = "application/pdf"
	}

	logger.Log.Info("Exporting deck", zap.String("filename", filename), zap.Int("size", len(body)))

	// Save PPTX to database if format is PPTX and export was successful
	if input.Format == "pptx" && res.StatusCode == http.StatusOK {
		if err := update.UpdateDeckPPT(deckId, body, filename); err != nil {
			logger.Log.Warn("Failed to save PPT to database, but export succeeded", zap.Error(err), zap.String("deck_id", deckId))
			// Continue even if DB save fails
		}
	}

	// Set headers and return binary data
	c.Header("Content-Type", mediaType)
	c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
	c.Data(res.StatusCode, mediaType, body)
}
