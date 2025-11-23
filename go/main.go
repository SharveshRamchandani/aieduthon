package main

import (
	"log"
	"os"

	auth "github.com/SharveshRamchandani/aieduthon.git/internal/Auth"
	"github.com/SharveshRamchandani/aieduthon.git/internal/config"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/migrations"
	"github.com/SharveshRamchandani/aieduthon.git/internal/server"
)

func main() {
	//Load the configurations for server
	cfs := config.LoadConfig()

	// Reconfigure the logger to the desired environment if provided
	if cfs.Env != "" {
		logger.LoadLogger(cfs.Env)
	}
	defer logger.Log.Sync()

	// Get all the credentials required to setup Google Authentication
	GoogleClientID := os.Getenv("GOOGLE_CLIENT_ID")
	GoogleSecretKey := os.Getenv("GOOGLE_CLIENT_SECRET")
	GoogleCallBack := os.Getenv("GOTH_GOOGLE_CALLBACK")
	if GoogleClientID == "" || GoogleCallBack == "" || GoogleSecretKey == ""{
		log.Fatalln("Please provide Google Client ID, Secret key, and the call back function")
		return
	}

	auth.SetUpgoth(GoogleClientID,GoogleSecretKey,GoogleCallBack)
	auth.InitStore(os.Getenv("SESSION_KEY"))

	//Establishing connection with DB
	db.ConnectDatabase()
	migrations.RunMigrations()

	//Starting server 
	server.StartServer(cfs)
}
