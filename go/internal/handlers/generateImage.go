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

func GenerateImages(c *gin.Context){
	var input interaction.GenerateImages

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to recieve input for generating image")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "Internal server error"})
		return
	}
	logger.Log.Debug("Received all the input for generating image")

	negative_prompt := ""
	num_images := 1
	use_cache := true

	var requestPayload = map[string]interface{}{
		"prompt" : input.PromptText,
		"width" : input.ImgWidth,
		"height" : input.ImgHeight,
		"negative_prompt" : negative_prompt,
		"num_images" : num_images,
		"use_cache" : use_cache,
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("failed to parse the input data")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "internal server error"})
		return
	}

	generateImage := fmt.Sprintf("%s/generate-image", os.Getenv("AI_URL"))
	logger.Log.Debug("generate image url", zap.String("url : ", generateImage))
	res, err := http.Post(generateImage, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		logger.Log.Error("failed to send data to generate image")
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