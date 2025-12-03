package post

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.uber.org/zap"
)

func CreateUser(user mongodb.Users){
	userCollection := get.GetCollections("users")


	ctx, cancel := context.WithTimeout(context.Background(), 5 * time.Second)
	defer cancel()

	result, err := userCollection.InsertOne(ctx,user)
	if err != nil{
		logger.Log.Error("Failed to insert the user into Db",
		zap.Error(err),
		zap.String("UserName: ", user.UserName),
		zap.String("User Email: ", user.Email),)
		return 
	}

	logger.Log.Debug("Successfully created user login",
		zap.Any("UserID: ", result.InsertedID),
	)
}