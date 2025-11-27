package handlers

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

func CreateJWTToken(extra map[string]any) (string, error) {
	claims := jwt.MapClaims{}

	for k, v := range extra {
		claims[k] = v
	}

	claims["iat"] = time.Now().Unix()
	claims["exp"] = time.Now().Add(24 * time.Hour).Unix()

	JwtStr := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return JwtStr.SignedString(JwtKey)
}