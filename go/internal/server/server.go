package server

import (
	"fmt"

	"github.com/SharveshRamchandani/aieduthon.git/internal/modals"
	"github.com/gin-gonic/gin"
)

func StartServer(cfs *modals.Config){
	router := gin.New()

	//add router function call

	//add logger success message

	err := router.Run(fmt.Sprintf(":%s",cfs.Port))
	if err != nil{
		//add logger error meassage
		fmt.Printf("failed to start server at port: %s",cfs.Port)
		return
	}
}