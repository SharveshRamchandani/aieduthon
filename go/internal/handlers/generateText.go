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

func GenerateText(c *gin.Context){
	var input interaction.GenerateText

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to receive the input for genrating text", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "Internal server error"})
		return
	}
	logger.Log.Debug("Successfully received input for gernerating text")

	if len(input.PromptText) < 1 {
		logger.Log.Error("Prompt is too short." ,zap.String("prompt : ", input.PromptText))
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "internal server error"})
		return
	}	

	max_length := 100
	temperature := 1.0
	use_cache := false

	var requestPayload = map[string]interface{}{
		"prompt" : input.PromptText,
		"context" : input.Context,
		"max_length" : max_length,
		"temperature" : temperature,
		"use_cache" : use_cache,
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("failed to parse the input data")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "internal server error"})
		return
	}

	generateText := fmt.Sprintf("%s/generate-text",os.Getenv("AI_URL"))
	res, err := http.Post(generateText, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		logger.Log.Error("failed to send data to generate text")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "internal server error"})
		return
	}

	var responseBody map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&responseBody); err != nil {
		logger.Log.Error("Failed to decode response from AI server", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	logger.Log.Info("Response data : ", zap.Any("Data: ", responseBody))

	c.JSON(res.StatusCode, responseBody)
}