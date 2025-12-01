package db

import (
	"context"
	"os"
	"time"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.uber.org/zap"
)

// global variables
var MongoClient *mongo.Client
var MongoDataBase *mongo.Database

func ConnectDatabase(){
	//creating context for the client function
	ctx, cancel := context.WithTimeout(context.Background(),10*time.Second)
	defer cancel()

	//creating a client mongo client instance
	client,err := mongo.Connect(ctx, options.Client().ApplyURI(os.Getenv("URI")))
	if err != nil{
		logger.Log.Error("Failed to connect to database ", zap.Error(err))
		return
	}

	//checking whether the client is functional and checking the connection
	if err := client.Ping(ctx,nil); err != nil{
		logger.Log.Error("Failed to Ping the Database connection", zap.Error(err))
		return
	}

	// assigning local to global variables
	MongoClient = client
	MongoDataBase = client.Database(os.Getenv("DBNAME"))
	
	logger.Log.Debug("The DB Connection was established successfully", 
		zap.String("DataBase -> ",MongoDataBase.Name()),
		zap.String("URI -> ", os.Getenv("URI")),
	)	
}