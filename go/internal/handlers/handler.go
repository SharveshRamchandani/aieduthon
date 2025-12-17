package handlers

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"os"
	"time"

	auth "github.com/SharveshRamchandani/aieduthon.git/internal/Auth"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db/get"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db/post"
	"github.com/SharveshRamchandani/aieduthon.git/internal/db/update"
	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/SharveshRamchandani/aieduthon.git/internal/modals/login"
	mongodb "github.com/SharveshRamchandani/aieduthon.git/internal/modals/mongoDB"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
	"go.uber.org/zap"
)

var JwtKey = []byte(os.Getenv("JWT_SECRET"))

func GoogleCallBackFunction(c *gin.Context) {
	user, err := gothic.CompleteUserAuth(c.Writer, c.Request)
	if err != nil {
		logger.Log.Error("Failed to complete user Auth", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"Error": err})
		return
	}

	if user.Email == "" {
		logger.Log.Error("Failed to fetch user's email")
		c.JSON(http.StatusBadRequest, gin.H{"Error": "Please provide a valid email!!"})
		return
	}

	//Add to DB if new user or verify if they are existing user
	exists, err := get.CheckUserExists(user.Email)
	if err != nil{
		logger.Log.Error("Failed to check the user's existance",
		zap.Error(err),)
		c.JSON(http.StatusInternalServerError, gin.H{"Error": "Internal Server Error"})
		return
	}

	if exists == nil{
		r := mongodb.Users{
			UserName: user.Name,
			Email: user.Email,
			GoogleID: user.UserID,
			AuthProvider: "google",
			Organisation: "",
			LastLogin: time.Now().Format("Monday, 02-Jan-06 15:04:05 MST"),
			Createdat: time.DateOnly,
		}
		post.CreateUser(r)
	}else{
		logger.Log.Debug("User already exists", zap.String("email", user.Email))
	}

	JwtToken, err := CreateJWTToken(map[string]any{
		"name":  user.Name,
		"ID":    user.UserID,
		"email": user.Email,
	})

	if err != nil {
		logger.Log.Error("Failed to create JWT token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server error"})
		return
	}

	session, _ := auth.Store.Get(c.Request, "session")
	session.Values["email"] = user.Email
	_ = session.Save(c.Request, c.Writer)

	frontendURL := os.Getenv("FRONTEND_URL")
	if frontendURL == "" {
		logger.Log.Error("FRONTEND_URL environment variable is not set")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server error"})
		return
	}

	JwtExp := time.Now().Add(24 * time.Hour).Unix()

	c.SetCookie(
		"jwt",
		JwtToken,
		int(JwtExp),
		"/",
		"localhost",
		false,
		true,
	)

	logger.Log.Info("Frontend URL loaded", zap.String("url", frontendURL))

	redirect := fmt.Sprintf("%s/home", frontendURL)
	c.Redirect(http.StatusSeeOther, redirect)
}

func Login(c *gin.Context){
	var Login login.Users

	if err := c.BindJSON(&Login); err != nil{
		logger.Log.Error("failed to read user data.", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error":"Internal server error"})
		return
	}

	exists, err := get.CheckUserExists(Login.UserEmail)
	if err != nil{
		logger.Log.Error("Failed to check the user's existance",
		zap.Error(err),)
		c.JSON(http.StatusInternalServerError, gin.H{"Error": "Internal Server Error"})
		return
	}

	if exists == nil {
		logger.Log.Error("User does not exist.", zap.String("Email: ", Login.UserEmail))
		c.JSON(http.StatusBadRequest, gin.H{"Error": "User not found"})
		return
	}

	hashed := sha256.Sum256([]byte(Login.Password))
	HexHash := hex.EncodeToString(hashed[:])

	if HexHash != exists.PasswdHash{
		logger.Log.Error("Password does not match", zap.String("User: ",Login.UserEmail))
		c.JSON(http.StatusBadRequest, gin.H{"Error" : "Password is incorrect"})
		return
	}

	JWTToken, err := CreateJWTToken(map[string]any{
		"Name": exists.UserName,
		"ID": exists.ID,
		"email": exists.Email,
	})

	if err != nil {
		logger.Log.Error("Failed to create JWT token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server error"})
		return
	}

	update.UpdateLoginTime(Login)

	JwtExp := time.Now().Add(24 * time.Hour).Unix()

	c.SetCookie(
		"jwt",
		JWTToken,
		int(JwtExp),
		"/",
		"localhost",
		false,
		true,
	)

	logger.Log.Debug("User successfully logged in", zap.String("User : ", exists.UserName))
	c.JSON(http.StatusAccepted, gin.H{"Message" : "Successfully LoggedIn"})
}

func SignUp(c *gin.Context){
	var signup login.SignUp

	if err := c.BindJSON(&signup); err != nil {
		logger.Log.Error("Failed to fetch the user details", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "Internal server error"})
		return
	}

	exists, err := get.CheckUserExists(signup.Email)
	if err != nil {
		logger.Log.Error("Failed to fetch user from DB" , zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Internal Server Error"})
		return
	}

	hashed := sha256.Sum256([]byte(signup.Password))
	HexHashed := hex.EncodeToString(hashed[:])

	if exists == nil{
		r := mongodb.Users{
			UserName: signup.Name,
			Email: signup.Email,
			PasswdHash: HexHashed,
			AuthProvider: "Local",
			Organisation: "",
			LastLogin: time.Now().Format("Monday, 02-Jan-06 15:04:05 MST"),
			Createdat: time.DateOnly,
		}
		post.CreateUser(r)
	}else {
		logger.Log.Debug("User already exists", zap.String("User : ", exists.UserName))
	}

	loginURL := os.Getenv("LOGIN_URL")
	if loginURL == ""{
		logger.Log.Error("Failed to fetch login url", zap.String("URL: ", loginURL))
		c.JSON(http.StatusInternalServerError, gin.H{"error" : "Internal server error"})
		return
	}

	logger.Log.Debug("Login URL: " + loginURL)
	logger.Log.Debug("User SignedUp successfully", zap.String("User: ", signup.Name), zap.String("Email: ", signup.Email))
	c.Redirect(http.StatusSeeOther, loginURL)
}