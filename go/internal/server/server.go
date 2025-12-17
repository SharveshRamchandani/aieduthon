package server

import (
	"fmt"

	cors "github.com/SharveshRamchandani/aieduthon.git/internal/Cors"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/modals"
	"github.com/SharveshRamchandani/aieduthon.git/internal/routes"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func StartServer(cfs *modals.Config){
	router := gin.New()

	cors.InitCors(router)

	//add router function call
	logger.Log.Info("Starting server ", zap.String("env->",cfs.Env), zap.String("port->",cfs.Port))
	routes.Routes(router)

	err := router.Run(fmt.Sprintf(":%s",cfs.Port))
	if err != nil{
		logger.Log.Error("failed to start the server", zap.String("error", err.Error()))
		return
	}
	logger.Log.Info("Server Started successfully at",zap.String("env->",cfs.Env), zap.String("port->",cfs.Port))
}