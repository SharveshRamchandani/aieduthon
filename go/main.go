package main

import (
	"github.com/SharveshRamchandani/aieduthon.git/internal/config"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/server"
)

func main() {
	//Load the configurations for server
	cfs := config.LoadConfig()

	//Load the Logger 
	logger.LoadLogger(cfs.Env)

	server.StartServer(cfs)
}