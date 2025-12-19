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

func GenerateDiagram(c *gin.Context){
	var input interaction.GenerateDiagram

	if err := c.BindJSON(&input); err != nil {
		logger.Log.Error("Failed to recieve input for generating diagrams")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "Internal server error"})
		return
	}
	logger.Log.Debug("Received all the input for generating diagrams")

	style := "animated"
	data := map[string]interface{}{}

	var requestPayload = map[string]interface{}{
		"diagram_type" : input.DiagramType,
		"description" : input.Description,
		"data" : data,
		"format" : input.Format,
		"style" : style,
	}

	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		logger.Log.Error("failed to parse the input data")
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "internal server error"})
		return
	}

	generateDiagram := fmt.Sprintf("%s/generate-diagram", os.Getenv("AI_URL"))
	logger.Log.Debug("generate diagram url", zap.String("url : ", generateDiagram))
	res, err := http.Post(generateDiagram, "application/json", bytes.NewBuffer(jsonData))
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