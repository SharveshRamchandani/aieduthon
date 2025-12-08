package middleware

import (
	"net/http"
	"strings"

	"github.com/SharveshRamchandani/aieduthon.git/internal/handlers"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"go.uber.org/zap"
)

func JWTMiddleWare() gin.HandlerFunc{
	return func(ctx *gin.Context) {
		var TokenString string

		auth := ctx.GetHeader("Authorization")
		if strings.HasPrefix(auth, "Bearer "){
			TokenString = strings.TrimPrefix(auth,"Bearer ")
		} else {
			if cookie, err := ctx.Cookie("jwt"); err == nil{
				TokenString = cookie
			}
		}

		if TokenString == "" {
            logger.Log.Debug("JWT token not found in request (user not authenticated)", 
                zap.String("path", ctx.Request.URL.Path))
            ctx.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized access"})
            return
        }

		parse, err := jwt.Parse(TokenString, func(t *jwt.Token) (interface{}, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                logger.Log.Error("JWT signing method mismatch", zap.String("method", t.Method.Alg()))
                return nil, jwt.ErrSignatureInvalid
            }
            return handlers.JwtKey, nil
        })

		if err != nil || !parse.Valid {
            logger.Log.Error("JWT token validation failed", zap.Error(err))
            ctx.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized access"})
            return
        }

		claims, ok := parse.Claims.(jwt.MapClaims)
        if !ok {
            logger.Log.Error("JWT claims extraction failed")
            ctx.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized access"})
            return
        }

        ctx.Set("claims", mapFromClaims(claims))
        ctx.Next()
	}
}

func mapFromClaims(c jwt.MapClaims) map[string]any{
	out := make(map[string]any)
	for k, v := range c{
		out[k] = v
	}
	return  out
}