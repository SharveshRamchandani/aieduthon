package config

import (
	"errors"
	"os"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/modals"
	"github.com/joho/godotenv"
	"go.uber.org/zap"
)

var (
	errfailedToLoadPORT = errors.New("failed to port from env")
	errfailedToLoadENV = errors.New("failed to environment type from env")
	cfs = &modals.Config{
			Port: "",
			Env: "",
		}
)

func LoadConfig() (*modals.Config) {
	// first load the config 
	err := godotenv.Load()
	if err != nil{
		logger.Log.Error("Failed to load env",zap.Error(err))
		return cfs
	}
	logger.Log.Debug("Successfully loaded env")

	//load port
	port := os.Getenv("PORT")
	if port == ""{
		logger.Log.Error("Failed to fetch port",zap.Error(err))
		return cfs
	}
	logger.Log.Debug("Port Loaded", zap.Any("port->",port))

	//load environment type
	env := os.Getenv("ENV")
	if env == "" {
		logger.Log.Error("Failed to fetch port",zap.Error(err))
		return cfs
	}
	logger.Log.Debug("Environment Loaded", zap.Any("env->",env))

	return &modals.Config{
		Port: port,
		Env: env,
	}
}