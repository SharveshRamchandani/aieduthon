package routes

import (
	"net/http"

	"github.com/SharveshRamchandani/aieduthon.git/internal/handlers"
	"github.com/SharveshRamchandani/aieduthon.git/internal/middleware"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
)

func Routes(r *gin.Engine) {

	r.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "The Router is working",
		})
	})

	r.GET("/auth/:provider", func(c *gin.Context) {
		provider := c.Param("provider")

		q := c.Request.URL.Query()
		q.Add("provider", provider)
		c.Request.URL.RawQuery = q.Encode()

		gothic.BeginAuthHandler(c.Writer, c.Request)
	})

	r.GET("/auth/:provider/callback", func(c *gin.Context) {
		provider := c.Param("provider")
		q := c.Request.URL.Query()
		q.Add("provider", provider)
		c.Request.URL.RawQuery = q.Encode()
		handlers.GoogleCallBackFunction(c)
	})

	r.GET("/auth/status", handlers.AuthStatus)

	r.GET("/auth/logout", handlers.Logout)
	r.GET("/login", handlers.Login)
	r.POST("/signup", handlers.SignUp)

	authorized := r.Group("/api")
	authorized.Use(middleware.JWTMiddleWare())
	{
		authorized.GET("/protected", func(c *gin.Context) {
			claims := c.MustGet("claims").(map[string]any)
			c.JSON(200, gin.H{"msg": "hello protected", "claims": claims})
		})
	}
}
