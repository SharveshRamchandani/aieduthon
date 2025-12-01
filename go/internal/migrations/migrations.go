package migrations

import (
	"context"
	"time"

	"github.com/SharveshRamchandani/aieduthon.git/internal/db"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"go.uber.org/zap"
)

func RunMigrations(){
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	modals := map[string]interface{}{
		"users" : mongodb.Users{},
		"analytics" : mongodb.Analytics{},
		"diagrams" : mongodb.Diagram{},
		"jobs" : mongodb.Job{},
		"media" : mongodb.Media{},
		"prompts" : mongodb.Prompt{},
		"quizzes" : mongodb.Quiz{},
		"slides" : mongodb.Slide{},
		"templates" : mongodb.Template{},
		"translations" : mongodb.Translation{},
	}


	for collectionName, modal := range modals{
		
		err := db.MongoDataBase.CreateCollection(ctx, collectionName)
		if err != nil && !alreadyexists(err){
			logger.Log.Error("failed to create collection", zap.String("collectionName: ", collectionName), zap.Error(err))
			return
		}

		if err := CreateIndexFeild(ctx, db.MongoDataBase.Collection(collectionName), modal); err != nil {
			logger.Log.Error("failed to create index to collection", zap.String("Collection: ", collectionName), zap.Error(err))
			return
		}
	}

	logger.Log.Info("Migrations are complete, DB is ready")
}

