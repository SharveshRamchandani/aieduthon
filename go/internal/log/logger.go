package logger

import (
	"fmt"

	"go.uber.org/zap"
)

// global variable for using the logger function in the whole project
var Log *zap.Logger

func LoadLogger(env string){
	var err error
	
	// checking the environment type
	if env == "Development"{
		Log, err = zap.NewDevelopment()
	}else if env == "Production"{
		Log, err = zap.NewProduction()
	}

	if err != nil{
		fmt.Println("failed to load Logger", err.Error())
		return
	}
	defer Log.Sync()

	Log.Info("Logger setup completed successfully! ", zap.String("Environment: ",env))
}