package handlers

import (
	"os"

	auth "github.com/SharveshRamchandani/aieduthon.git/internal/Auth"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
)

var JwtKey = []byte(os.Getenv("JWT_SECRET"))
var FrontendURL = os.Getenv("FRONTEND_URL")

func GoogleLoginHandler(c *gin.Context){
	auth.GinHandler(gothic.BeginAuthHandler)(c)
}

