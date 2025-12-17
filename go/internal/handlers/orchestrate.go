package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	interaction "github.com/SharveshRamchandani/aieduthon.git/internal/modals/Interaction"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func Orchestrate(c *gin.Context) {
	var input interaction.ReceivedPrompts

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to receive the user input", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	logger.Log.Debug("Received user input. Calling orchestrate")

	// Validate prompt
	if len(input.Prompt) < 3 {
		logger.Log.Error("Prompt is too short", zap.String("prompt", input.Prompt))
		c.JSON(http.StatusBadRequest, gin.H{"error": "Prompt must be at least 3 characters long"})
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
					// Use email as fallback if ID is not available
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

	// Set defaults for optional fields
	if input.Locale == "" {
		input.Locale = "en"
	}
	if input.QuizType == "" {
		input.QuizType = "comprehensive"
	}
	if input.PresentationStyle == "" {
		input.PresentationStyle = "educational"
	}

	// Create the request payload matching Python's expected format
	requestPayload := map[string]interface{}{
		"prompt":             input.Prompt,
		"userId":             input.UserId,
		"locale":             input.Locale,
		"generate_images":    input.GenerateImages,
		"generate_diagrams":  input.GenerateDiagrams,
		"quiz_type":          input.QuizType,
		"presentation_style": input.PresentationStyle,
	}

	// Add optional fields only if they have values
	if input.Context != nil && len(input.Context) > 0 {
		requestPayload["context"] = input.Context
	}
	if input.EstimatedSlides != nil && *input.EstimatedSlides >= 3 {
		requestPayload["estimated_slides"] = *input.EstimatedSlides
	}
	if input.QuizQuestions != nil && *input.QuizQuestions >= 1 {
		requestPayload["quiz_questions"] = *input.QuizQuestions
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
	logger.Log.Debug("Successfully parsed struct to json", zap.String("data", string(jsonData)))

	orchestrateURL := fmt.Sprintf("%s/orchestrate", os.Getenv("AI_URL"))
	logger.Log.Debug("The AI url", zap.String("url", orchestrateURL))

	res, err := http.Post(orchestrateURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		logger.Log.Error("Failed to receive the data from ai server", zap.Error(err))
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

	// Return the response with the same status code
	c.JSON(res.StatusCode, responseBody)
}
