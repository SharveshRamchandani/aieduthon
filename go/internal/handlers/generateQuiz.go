package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/update"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	interaction "github.com/SharveshRamchandani/aieduthon.git/internal/modals/Interaction"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func GenerateQuiz(c *gin.Context) {
	deckId := c.Param("deck_id")
	if deckId == "" {
		logger.Log.Error("Deck ID is required")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Deck ID is required"})
		return
	}

	var input interaction.GenerateQuiz

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to receive input for generating quiz", zap.Error(err))
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
	if input.QuizType == "" {
		input.QuizType = "comprehensive"
	}

	// Check if PDF download is requested
	downloadFormat := c.Query("download")
	isPDFRequest := downloadFormat == "pdf"

	logger.Log.Debug("Generating quiz",
		zap.String("deck_id", deckId),
		zap.String("user_id", input.UserId),
		zap.String("quiz_type", input.QuizType),
		zap.Bool("pdf_request", isPDFRequest))

	// Create request payload
	requestPayload := map[string]interface{}{
		"userId":    input.UserId,
		"quiz_type": input.QuizType,
	}
	if input.Difficulty != "" {
		requestPayload["difficulty"] = input.Difficulty
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("Failed to parse struct to json", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Build URL with query parameter if PDF is requested
	quizURL := fmt.Sprintf("%s/slides/%s/quizzes", os.Getenv("AI_URL"), deckId)
	if isPDFRequest {
		quizURL += "?download=pdf"
	}
	logger.Log.Debug("AI service URL", zap.String("url", quizURL))

	req, err := http.NewRequest("POST", quizURL, bytes.NewBuffer(jsonData))
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

	// Check if response is PDF (based on Content-Type header)
	contentType := res.Header.Get("Content-Type")
	if contentType == "application/pdf" || isPDFRequest {
		// Read response body (PDF file)
		body, err := io.ReadAll(res.Body)
		if err != nil {
			logger.Log.Error("Failed to read response from AI server", zap.Error(err))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		// Get filename from Content-Disposition header or use default
		filename := "quiz.pdf"
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

		logger.Log.Info("Generating quiz PDF", zap.String("filename", filename), zap.Int("size", len(body)))

		// Set headers and return PDF binary data
		c.Header("Content-Type", "application/pdf")
		c.Header("Content-Disposition", fmt.Sprintf(`attachment; filename="%s"`, filename))
		c.Data(res.StatusCode, "application/pdf", body)
		return
	}

	// Default JSON response
	var responseBody map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&responseBody); err != nil {
		logger.Log.Error("Failed to decode response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	logger.Log.Info("Response data", zap.Any("Data", responseBody))

	// Update deck quiz refs in database if quiz_ids are present
	if quizIDs, ok := responseBody["quiz_ids"].([]interface{}); ok && len(quizIDs) > 0 {
		quizRefs := make([]string, 0, len(quizIDs))
		for _, id := range quizIDs {
			if idStr, ok := id.(string); ok {
				quizRefs = append(quizRefs, idStr)
			}
		}
		if len(quizRefs) > 0 {
			if err := update.UpdateDeckQuizRefs(deckId, quizRefs); err != nil {
				logger.Log.Warn("Failed to update deck quiz refs, but quiz generation succeeded", zap.Error(err), zap.String("deck_id", deckId))
				// Continue even if DB update fails
			}
		}
	}

	// Return the response with the same status code
	c.JSON(res.StatusCode, responseBody)
}
