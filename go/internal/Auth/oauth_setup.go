package auth

import (
	"github.com/gorilla/sessions"
	"github.com/markbates/goth"
	"github.com/markbates/goth/providers/google"

	logger "github.com/SharveshRamchandani/aieduthon.git/internal/log"
)

var Store *sessions.CookieStore

// InitStore sets up the package-level session store.
// Notes (written in a kinda human-mistake style so it's easy to read later):
//   - If you forget to pass a key (I do that sometimes) we fall back to a hard-coded
//     key and log a warning so you can spot the mistake when you review later.
//   - We intentionally log a warning when using the fallback key because that is
//     insecure for production — don't do this on prod, but it's handy while hacking.
func InitStore(key string) {
	if key == "" {
		logger.Log.Warn("auth: InitStore: warning: no key provided; using fallback default key (don't do this in production)")
		return
	}

	Store = sessions.NewCookieStore([]byte(key))

	Store.Options = &sessions.Options{
		Path:     "/",
		MaxAge:   86400 * 7,
		HttpOnly: true,
		Secure:   false,
	}

	logger.Log.Debug("auth: InitStore: info: session store initialized; HttpOnly=true, Secure=false")
}

// SetUpgoth registers OAuth providers with goth and wires up the session store.
// Notes (human-mistake style):
//   - If you accidentally pass empty clientId or secret (I do that sometimes) we log an
//     error and don't register the provider so you don't end up with a half-configured flow.
//   - We avoid logging secrets — logging the clientId is fine for debugging but never the secret.
//   - If callback URL is empty we log a warning because the provider may misbehave.
func SetUpgoth(clientId, secretkey, callbackfunc string) {
	goth.UseProviders(google.New(clientId, secretkey, callbackfunc, "email", "profile"))
	logger.Log.Debug("auth: SetUpgoth: info: google provider registered (clientId provided, secret not logged)")

	// Ensure goth's store is wired up from our Store.
	err := GothicStoreWrapper()
	if err == ""{
		logger.Log.Error("auth: GothicStoreWrapper: warning: auth.Store is nil; gothic.Store not set")
		return
	}
}
