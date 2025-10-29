package config

import (
	"errors"
	"fmt"
	"os"

	"github.com/SharveshRamchandani/aieduthon.git/internal/modals"
	"github.com/joho/godotenv"
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
		fmt.Println("Failed to load env", err)
		return cfs
	}
	fmt.Println("Successfully loaded env")

	//load port
	port := os.Getenv("PORT")
	if port == ""{
		fmt.Println("Failed to fetch port", errfailedToLoadPORT)
		return cfs
	}
	fmt.Println("Port Loaded", port)

	//load environment type
	env := os.Getenv("ENV")
	if env == "" {
		fmt.Println("Failed to fetch port", errfailedToLoadENV)
		return cfs
	}
	fmt.Println("Environment Loaded", env)

	return &modals.Config{
		Port: port,
		Env: env,
	}
}