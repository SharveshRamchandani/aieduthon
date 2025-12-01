package get

import (
	"github.com/SharveshRamchandani/aieduthon.git/internal/db"
	"go.mongodb.org/mongo-driver/mongo"
)

func GetCollections(name string) (*mongo.Collection){
	return db.MongoDataBase.Collection(name)
}