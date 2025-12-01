package main

import (
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

	//Establishing connection with DB
	db.ConnectDatabase()

	migrations.RunMigrations()

	//Starting server 
	server.StartServer(cfs)
}
