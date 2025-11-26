package middleware

import (
	"net/http"
	"strings"

	"github.com/SharveshRamchandani/aieduthon.git/internal/handlers"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
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

		if TokenString == ""{
			logger.Log.Error("UnAuthorized Jwt Token not found!!")
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error": "Unauthorized access"})
			return
		}

		parse, err := jwt.Parse(TokenString, func(t *jwt.Token) (interface{}, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok{
				return nil, jwt.ErrHashUnavailable
			}
			return handlers.JwtKey, nil
		})

		if err != nil || !parse.Valid{
			logger.Log.Error("UnAuthorized Jwt Token not found!!")
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error": "Unauthorized access"})
			return
		}

		claims, ok := parse.Claims.(jwt.MapClaims)
		if !ok{
			logger.Log.Error("UnAuthorized Jwt Token not found!!")
			ctx.JSON(http.StatusUnauthorized, gin.H{"Error": "Unauthorized access"})
			return
		}

		ctx.Set("claims" , mapFromClaims(claims))
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