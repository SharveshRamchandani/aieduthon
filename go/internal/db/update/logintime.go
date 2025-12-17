package update

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/modals/login"
	"go.mongodb.org/mongo-driver/bson"
	"go.uber.org/zap"
)

func UpdateLoginTime(user login.Users) {
	filter := bson.M{"email": user.UserEmail}
	Update := bson.M{"$set" : bson.M{"lastlogin" : time.Now().Format("Monday, 02-Jan-06 15:04:05 MST")}}

	userCollection := get.GetCollections("users")
	
	_, err := userCollection.UpdateOne(context.Background(), filter, Update)
	if err != nil {
		logger.Log.Error("Failed to update login time of user", zap.Any("Filter", filter), zap.Any("Update" , Update))
		return
	}
} 