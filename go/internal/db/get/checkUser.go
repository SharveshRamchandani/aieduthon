package get

import (
	"context"
	"time"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.uber.org/zap"
)

func CheckUserExists(email string) (*mongodb.Users, error) {
	c, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	collection := GetCollections("users")
	var users mongodb.Users

	err := collection.FindOne(c, bson.M{"email": email}).Decode(&users)
	if err != nil {
		// If document not found, this is NORMAL for new users — log as debug, not error.
		if err == mongo.ErrNoDocuments {
			logger.Log.Debug("User not found in database (new user)", zap.String("email", email))
			return nil, nil
		}

		// Any OTHER error is a real problem — log as ERROR.
		logger.Log.Error("Failed to query user from database",
			zap.Error(err),
			zap.String("collection", collection.Name()),
			zap.String("email", email))
		return nil, err
	}

	// User found successfully.
	logger.Log.Debug("User found in database", zap.String("email", email))
	return &users, nil
}
