package main

import (
	"github.com/SharveshRamchandani/aieduthon.git/internal/config"
	"github.com/SharveshRamchandani/aieduthon.git/internal/server"
)

func main() {
	//Load the configurations for server
	cfs := config.LoadConfig()


	server.StartServer(cfs)
}