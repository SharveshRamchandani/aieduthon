package mongodb

type Users struct{
	ID string `bson:"_id,omitempty" json:"id"`
	UserName string `bson:"name" json:"name" unique:"true"`
	Email string `bson:"email" json:"email" unique:"true"`
	PasswdHash string `bson:"passwdhash" json:"passwdhash"`
	Organisation string `bson:"orgaanisation" json:"organisation"`
	LastLogin string `bson:"lastlogin" json:"lastlogin"`
	Createdat string `bson:"createdat" json:"created_at"`
}