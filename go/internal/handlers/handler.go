package handlers

import (
	"fmt"
	"net/http"
	"os"

	auth "github.com/SharveshRamchandani/aieduthon.git/internal/Auth"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
	"go.uber.org/zap"
)

var JwtKey = []byte(os.Getenv("JWT_SECRET"))

func GoogleCallBackFunction(c *gin.Context) {
	user, err := gothic.CompleteUserAuth(c.Writer, c.Request)
	if err != nil {
		logger.Log.Error("Failed to complete user Auth", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"Error": err})
		return
	}

	if user.Email == "" {
		logger.Log.Error("Failed to fetch user's email")
		c.JSON(http.StatusBadRequest, gin.H{"Error": "Please provide a valid email!!"})
		return
	}

	//Add to DB if new user or verify if they are existing user

	JwtToken, err := CreateJWTToken(map[string]any{
		"name":  user.Name,
		"ID":    user.UserID,
		"email": user.Email,
	})

	if err != nil {
		logger.Log.Error("Failed to create JWT token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server error"})
		return
	}

	session, _ := auth.Store.Get(c.Request, "session")
	session.Values["email"] = user.Email
	_ = session.Save(c.Request, c.Writer)

	frontendURL := os.Getenv("FRONTEND_URL")
	if frontendURL == "" {
		logger.Log.Error("FRONTEND_URL environment variable is not set")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server error"})
		return
	}

	logger.Log.Info("Frontend URL loaded", zap.String("url", frontendURL))

	redirect := fmt.Sprintf("%s/home?token=%s", frontendURL, JwtToken)
	c.Redirect(http.StatusSeeOther, redirect)
}
