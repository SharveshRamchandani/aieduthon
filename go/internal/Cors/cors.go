package cors

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func InitCors(r *gin.Engine) {
	corsConfig := cors.Config{
		AllowOrigins:  []string{"http://localhost:8080"},
		AllowMethods:  []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:  []string{"Origin", "Content-Type", "Authorization"},
		ExposeHeaders: []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge: 86400,
	}
	r.Use(cors.New(corsConfig))
}