package server

import (
	"fmt"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/modals"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func StartServer(cfs *modals.Config){
	router := gin.New()

	//add router function call

	logger.Log.Info("Starting server ", zap.String("env->",cfs.Env), zap.String("port->",cfs.Port))

	err := router.Run(fmt.Sprintf(":%s",cfs.Port))
	if err != nil{
		logger.Log.Error("failed to start the server", zap.String("error", err.Error()))
		return
	}
	logger.Log.Info("Server Started successfully at",zap.String("env->",cfs.Env), zap.String("port->",cfs.Port))
}