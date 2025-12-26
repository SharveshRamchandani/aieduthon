package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/post"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db/update"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	interaction "github.com/SharveshRamchandani/aieduthon.git/internal/modals/Interaction"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
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

	// Store prompt in database before calling AI
	promptID, err := post.CreatePrompt(
		input.UserId,
		input.Prompt,
		input.Locale,
		input.Context,
	)
	if err != nil {
		logger.Log.Error("Failed to create prompt in database", zap.Error(err))
		// Continue anyway - AI might still create it
	} else {
		logger.Log.Debug("Prompt created in database", zap.String("prompt_id", promptID))
	}

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
	logger.Log.Info("Response data : ", zap.Any("Data: ", responseBody))

	// Store data returned from AI (since AI now returns data instead of storing)
	var actualPromptID string
	var actualDeckID string

	// 1. Store prompt data if present
	if promptData, ok := responseBody["prompt_data"].(map[string]interface{}); ok {
		promptID, err := post.CreatePrompt(
			promptData["userId"].(string),
			promptData["prompt_text"].(string),
			promptData["locale"].(string),
			promptData["context"].(map[string]interface{}),
		)
		if err != nil {
			logger.Log.Warn("Failed to store prompt data", zap.Error(err))
		} else {
			actualPromptID = promptID
			responseBody["promptId"] = promptID
		}
	}

	// 2. Store deck data if present
	if deckData, ok := responseBody["deck_data"].(map[string]interface{}); ok {
		// Use actual prompt ID if we just created it
		promptIDForDeck := actualPromptID
		if promptIDForDeck == "" {
			if pid, ok := responseBody["promptId"].(string); ok {
				promptIDForDeck = pid
			}
		}
		if promptIDForDeck == "" {
			// Use the prompt_id from deck_data if available
			if pid, ok := deckData["promptId"].(string); ok {
				promptIDForDeck = pid
			}
		}

		deckID, err := post.CreateSlideDeck(promptIDForDeck, input.UserId, deckData)
		if err != nil {
			logger.Log.Warn("Failed to store deck data", zap.Error(err))
		} else {
			actualDeckID = deckID
			responseBody["deckId"] = deckID
		}
	} else if deckID, ok := responseBody["deckId"].(string); ok && deckID != "" {
		actualDeckID = deckID
	}

	// 3. Store quiz data if present
	quizIDs := make([]string, 0)
	if quizDataList, ok := responseBody["quiz_data"].([]interface{}); ok && len(quizDataList) > 0 && actualDeckID != "" {
		for _, quizData := range quizDataList {
			if quizMap, ok := quizData.(map[string]interface{}); ok {
				quizID, err := post.CreateQuiz(actualDeckID, quizMap)
				if err != nil {
					logger.Log.Warn("Failed to store quiz data", zap.Error(err), zap.String("deck_id", actualDeckID))
				} else {
					quizIDs = append(quizIDs, quizID)
				}
			}
		}
		// Update response with actual quiz IDs
		if len(quizIDs) > 0 {
			responseBody["quizIds"] = quizIDs
		}
	}

	// 4. Store speaker notes if present
	if speakerNotesData, ok := responseBody["speaker_notes_data"].([]interface{}); ok && actualDeckID != "" {
		// Convert to SpeakerNote structs
		notes := make([]mongodb.SpeakerNote, 0, len(speakerNotesData))
		for i, noteData := range speakerNotesData {
			if noteMap, ok := noteData.(map[string]interface{}); ok {
				note := mongodb.SpeakerNote{
					SlideIndex: i,
				}
				if title, ok := noteMap["slide_title"].(string); ok {
					note.SlideTitle = title
				}
				if points, ok := noteMap["main_points"].([]interface{}); ok {
					note.KeyPoints = make([]string, len(points))
					for j, p := range points {
						if str, ok := p.(string); ok {
							note.KeyPoints[j] = str
						}
					}
				}
				if examples, ok := noteMap["examples"].([]interface{}); ok {
					note.Examples = make([]string, len(examples))
					for j, e := range examples {
						if str, ok := e.(string); ok {
							note.Examples[j] = str
						}
					}
				}
				notes = append(notes, note)
			}
		}
		if len(notes) > 0 {
			if err := update.UpdateDeckSpeakerNotes(actualDeckID, notes); err != nil {
				logger.Log.Warn("Failed to store speaker notes", zap.Error(err), zap.String("deck_id", actualDeckID))
			}
		}
	}

	// 5. Update deck with media refs if present
	if actualDeckID != "" {
		if mediaRefs, ok := responseBody["media_refs"]; ok {
			if diagramRefs, ok := responseBody["diagram_refs"]; ok {
				if mediaMetadata, ok := responseBody["media_metadata"]; ok {
					if err := update.UpdateDeckMediaRefs(actualDeckID, mediaRefs, diagramRefs, mediaMetadata); err != nil {
						logger.Log.Warn("Failed to update deck media refs", zap.Error(err), zap.String("deck_id", actualDeckID))
					}
				}
			}
		}

		// 6. Update quiz refs if present
		if quizIDs, ok := responseBody["quizIds"].([]interface{}); ok && len(quizIDs) > 0 {
			quizRefs := make([]string, 0, len(quizIDs))
			for _, id := range quizIDs {
				if idStr, ok := id.(string); ok && idStr != "" {
					quizRefs = append(quizRefs, idStr)
				}
			}
			if len(quizRefs) > 0 {
				if err := update.UpdateDeckQuizRefs(actualDeckID, quizRefs); err != nil {
					logger.Log.Warn("Failed to update deck quiz refs", zap.Error(err), zap.String("deck_id", actualDeckID))
				}
			}
		}
	}

	// Return the response with the same status code
	c.JSON(res.StatusCode, responseBody)
}
