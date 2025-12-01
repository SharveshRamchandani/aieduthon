package migrations

import (
	"context"
	"reflect"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func CreateIndexFeild(ctx context.Context, collectionName *mongo.Collection, modal interface{}) (error) {
	val := reflect.TypeOf(modal)
	for i :=0; i < val.NumField(); i++{
		field := val.Field(i)
		if field.Tag.Get("unique") == "true"{
			fieldName := field.Tag.Get("bson")
			if fieldName == ""{
				fieldName = field.Name
			}

			opts := options.Index().SetUnique(true)
			index := mongo.IndexModel{
				Keys: bson.D{{Key: fieldName, Value: 1}},
				Options: opts,
			}

			_, err := collectionName.Indexes().CreateOne(ctx, index)
			if err != nil{
				return err
			}
		}
	}
	return nil
}