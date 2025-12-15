package mongodb

import "time"

// AICache represents cached AI generation results
type AICache struct {
	ID        string                 `bson:"_id,omitempty" json:"id"`
	CacheKey  string                 `bson:"cache_key" json:"cache_key"`
	Result    interface{}            `bson:"result" json:"result"` // Can be String, Array, or Object
	Metadata  map[string]interface{} `bson:"metadata" json:"metadata"`
	Type      string                 `bson:"type,omitempty" json:"type,omitempty"` // "text", "image", "stock_image"
	TTL       int64                  `bson:"ttl" json:"ttl"`                       // timestamp for expiration
	CreatedAt time.Time              `bson:"created_at" json:"created_at"`
}
