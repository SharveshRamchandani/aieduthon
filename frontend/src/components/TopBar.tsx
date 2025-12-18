"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Home, LogOut, Menu, Moon, Sparkles, Sun, User, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

import ProfileModal from "@/components/ProfileModal";
import SettingsModal from "@/components/SettingsModal";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";

const TopBar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showDesktopDropdown, setShowDesktopDropdown] = useState(false);
  const desktopDropdownRef = useRef<HTMLDivElement>(null);
  const { isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const toggleMenu = () => setIsOpen((prev) => !prev);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        desktopDropdownRef.current &&
        !desktopDropdownRef.current.contains(event.target as Node)
      ) {
        setShowDesktopDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    try {
      logout();
      setShowDesktopDropdown(false);
      navigate("/");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const getUserInitials = () => {
    if (user?.name) {
      return user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase();
    }
    if (user?.email) return user.email.charAt(0).toUpperCase();
    return "U";
  };

  const NavButtons = (
    <>
      {user && (
        <>
          <Button
            variant="ghost"
            onClick={() => navigate("/home")}
            className="flex items-center gap-2"
          >
            <Home className="h-4 w-4" />
            Home
          </Button>
          <Button
            variant="ghost"
            onClick={() => navigate("/ai-test")}
            className="flex items-center gap-2"
          >
            <Sparkles className="h-4 w-4" />
            AI Test
          </Button>
        </>
      )}
    </>
  );

  return (
    <>
      <div className="fixed top-0 left-0 right-0 flex justify-center py-6 px-4 z-50 bg-background">
        <div className="flex items-center justify-between px-6 py-3 bg-background rounded-full shadow-lg w-full max-w-3xl border border-border">
          {/* Brand */}
          <div className="flex items-center gap-2">
            <motion.div
              className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              whileHover={{ rotate: 8 }}
              transition={{ duration: 0.25 }}
            />
            <span className="text-xl font-bold tracking-tight text-foreground">
              SlideGen
            </span>
          </div>

          {/* Center nav (desktop) */}
          <div className="hidden md:flex items-center gap-4">{NavButtons}</div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="rounded-full"
            >
              {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>

            {user ? (
              <div className="relative" ref={desktopDropdownRef}>
                <button
                  onClick={() => setShowDesktopDropdown((s) => !s)}
                  className="px-3 py-1 rounded-full border border-border flex items-center gap-2 hover:bg-muted"
                >
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-primary-foreground text-sm font-medium">
                      {getUserInitials()}
                    </span>
                  </div>
                  <span className="text-sm font-medium">
                    {user.name || user.email?.split("@")[0] || "User"}
                  </span>
                </button>

                {showDesktopDropdown && (
                  <div className="absolute right-0 mt-2 w-64 bg-card rounded-lg shadow-lg border border-border z-50">
                    <div className="p-4 border-b border-border">
                      <p className="text-sm font-medium">
                        {user.name || "User"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {user.email || "user@example.com"}
                      </p>
                    </div>
                    <div className="p-1">
                      <button
                        onClick={() => {
                          setShowProfileModal(true);
                          setShowDesktopDropdown(false);
                        }}
                        className="flex items-center w-full px-2 py-2 text-sm hover:bg-accent rounded-sm transition-colors duration-200 text-foreground"
                      >
                        <User className="mr-2 h-4 w-4" />
                        <span>Profile</span>
                      </button>
                      <button
                        onClick={() => {
                          setShowSettingsModal(true);
                          setShowDesktopDropdown(false);
                        }}
                        className="flex items-center w-full px-2 py-2 text-sm hover:bg-accent rounded-sm transition-colors duration-200 text-foreground"
                      >
                        <Sparkles className="mr-2 h-4 w-4" />
                        <span>Settings</span>
                      </button>
                    </div>
                    <div className="px-2 pb-2 flex items-center justify-between">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleTheme}
                        className="rounded-full"
                      >
                        {isDark ? (
                          <Sun className="h-4 w-4" />
                        ) : (
                          <Moon className="h-4 w-4" />
                        )}
                      </Button>
                      <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm transition-colors duration-200 text-foreground"
                      >
                        <LogOut className="h-4 w-4" />
                        <span>Log out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Button onClick={() => navigate("/login")} variant="default" size="sm">
                Sign In
              </Button>
            )}

            {/* Mobile menu toggle */}
            <motion.button
              className="md:hidden flex items-center"
              onClick={toggleMenu}
              whileTap={{ scale: 0.92 }}
            >
              <Menu className="h-6 w-6 text-foreground" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed inset-0 bg-background z-40 pt-24 px-6 md:hidden"
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
          >
            <div className="flex items-center justify-between mb-6">
              <span className="text-lg font-semibold">Menu</span>
              <button onClick={toggleMenu} className="p-2 rounded-full hover:bg-muted">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex flex-col gap-2">{NavButtons}</div>

              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleTheme}
                  className="rounded-full"
                >
                  {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </Button>

                {user ? (
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => {
                      setShowProfileModal(true);
                      toggleMenu();
                    }}
                  >
                    Profile
                  </Button>
                ) : (
                  <Button
                    variant="default"
                    className="flex-1"
                    onClick={() => {
                      navigate("/login");
                      toggleMenu();
                    }}
                  >
                    Sign In
                  </Button>
                )}
              </div>

              {user && (
                <Button
                  variant="ghost"
                  onClick={() => {
                    handleLogout();
                    toggleMenu();
                  }}
                  className="flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Profile Modal */}
      <ProfileModal open={showProfileModal} onOpenChange={setShowProfileModal} />

      {/* Settings Modal */}
      <SettingsModal open={showSettingsModal} onOpenChange={setShowSettingsModal} />
    </>
  );
};

export { TopBar };



