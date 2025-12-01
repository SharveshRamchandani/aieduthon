package logger

import (
	"strings"

	"go.uber.org/zap"
)

var Log *zap.Logger

// to init the global logger
func LoadLogger(env string) {
	var err error

	normalized := strings.ToLower(strings.TrimSpace(env))

	// checking the environment (development or production)
	switch normalized {
	case "development", "dev":
		Log, err = zap.NewDevelopment()
	case "production", "prod":
		Log, err = zap.NewProduction()
	default:
		// default to development if unknown or empty
		Log, err = zap.NewDevelopment()
		normalized = "development"
	}

	if err != nil {
		panic("Failed to Initialize Logger: " + err.Error())
	}

	Log.Info("Logger Initialized ", zap.String("Environment", normalized))
}
