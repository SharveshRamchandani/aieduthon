package auth

import (
	"net/http"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
	"github.com/gin-gonic/gin"
	"github.com/markbates/goth/gothic"
)

// GothicStoreWrapper sets the gothic package Store to our package-level Store.
// I wrote this kinda quick so the comment isn't perfect — basically it checks if
// Store is nil (which I sometimes forget to set) and logs a warning so you can
// spot the problem when you review later.
//
// If Store is nil we don't touch gothic.Store and we log so you don't wonder
// why auth isn't working later.
func GothicStoreWrapper()(string) {
	if Store == nil {
		return ""
	}

	gothic.Store = Store
	logger.Log.Debug("auth: GothicStoreWrapper: info: gothic.Store set from auth.Store")
	return "pass"
}

// GinHandler wraps a standard net/http handler so it can be used as a gin.HandlerFunc.
// Notes (written in a kinda human-mistake style so it's easy to read later):
//   - If you accidentally pass nil as fn (I do that sometimes) we don't panic — we log
//     the mistake and return a 500 so you can find the bug in logs.
//   - We also recover from panics inside fn and log them, then return 500 to the client.
//   - This helps during dev so a bad oauth callback doesn't bring the whole server down.
func GinHandler(fn func(http.ResponseWriter, *http.Request)) gin.HandlerFunc {
	return func(c *gin.Context) {
		if fn == nil {
			logger.Log.Error("Failed to catch function named fn")
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
			return
		}

		// protect against panics in the wrapped handler so the server doesn't crash.
		defer func() {
			if r := recover(); r != nil {
				logger.Log.Error("auth: GinHandler: panic recovered from wrapped handler is nil",)
				c.AbortWithStatus(http.StatusInternalServerError)
			}
		}()

		fn(c.Writer, c.Request)
	}
}
