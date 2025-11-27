package auth

import (
	"fmt"
	"net/http"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
)

func GothicStoreWrapper() {
	if Store == nil {
		logger.Log.Error("auth: GothicStoreWrapper: CRITICAL ERROR: auth.Store is nil; InitStore() must be called BEFORE SetUpgoth()")
		return
	}

	gothic.Store = Store
	logger.Log.Debug("auth: GothicStoreWrapper: info: gothic.Store set from auth.Store successfully")
}

func GinHandler(fn func(http.ResponseWriter, *http.Request)) gin.HandlerFunc {
	return func(c *gin.Context) {
		if fn == nil {
			logger.Log.Error("auth: GinHandler: error: nil handler function provided; check where this middleware is used")
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
			return
		}

		defer func() {
			if r := recover(); r != nil {
				logger.Log.Error("auth: GinHandler: panic recovered from wrapped handler" + fmt.Sprintf("%v",r))
				c.AbortWithStatus(http.StatusInternalServerError)
			}
		}()

		fn(c.Writer, c.Request)
	}
}
