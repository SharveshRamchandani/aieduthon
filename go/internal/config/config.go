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
		// add logger error message
		fmt.Println("ERROR (Could not load environment variables): ", err.Error())
		return cfs
	}
	// add logger success message

	//load port
	port := os.Getenv("PORT")
	if port == ""{
		//add logger error message
		fmt.Println("Failed to load Port: ", errfailedToLoadPORT)
		return cfs
	}
	//add logger sucess message

	//load environment type
	env := os.Getenv("ENV")
	if env == "" {
		//add logger error message
		fmt.Println("Failed to load ENV",errfailedToLoadPORT)
		return cfs
	}
	//add logger success message

	return &modals.Config{
		Port: port,
		Env: env,
	}
}