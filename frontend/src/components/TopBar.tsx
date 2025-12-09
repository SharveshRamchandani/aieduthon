"use client"

import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
// import { Menu, X, Moon, Sun, LogOut, User } from "lucide-react"
import { Moon, Sun, LogOut, User, Home, Sparkles, Menu, X, Settings } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import ProfileModal from '@/components/ProfileModal';
import SettingsModal from '@/components/SettingsModal';

const TopBar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showDesktopDropdown, setShowDesktopDropdown] = useState(false);
  const desktopDropdownRef = useRef<HTMLDivElement>(null);
  const { isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const toggleMenu = () => setIsOpen(!isOpen)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (desktopDropdownRef.current && !desktopDropdownRef.current.contains(event.target as Node)) {
        setShowDesktopDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      logout();
      setShowDesktopDropdown(false);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user?.name) {
      return user.name
        .split(' ')
        .map(name => name[0])
        .join('')
        .toUpperCase();
    }
    
    if (user?.email) {
      return user.email.charAt(0).toUpperCase();
    }
    
    return 'U';
  };

  return (
    <>
      <div className="fixed top-0 left-0 right-0 flex justify-center py-6 px-4 z-50">
        <div className="flex items-center justify-between px-6 py-3 bg-background rounded-full shadow-lg w-full max-w-3xl border border-border">
          <div className="flex items-center">
            <motion.div
              className="w-8 h-8 mr-2"
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              whileHover={{ rotate: 10 }}
              transition={{ duration: 0.3 }}
            >
              {/* logo / icon could go here */}
            </motion.div>
            <span className="text-xl font-bold tracking-tight text-foreground">SlideGen</span>
          </div>
          
          {/* Centered Navigation */}
          <div className="absolute left-1/2 transform -translate-x-1/2 hidden md:block">
            <div className="flex items-center gap-4">
              {user && (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => navigate('/home')}
                    className="flex items-center gap-2"
                  >
                    <Home className="h-4 w-4" />
                    Home
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => navigate('/ai-test')}
                    className="flex items-center gap-2"
                  >
                    <Sparkles className="h-4 w-4" />
                    AI Test
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Desktop CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="relative" ref={desktopDropdownRef}>
                {/* Profile Button with consistent styling */}
                <button
                  onClick={() => setShowDesktopDropdown(!showDesktopDropdown)}
                  className={`px-3 py-1 rounded-full border border-border flex items-center space-x-2 ${
                    showDesktopDropdown
                      ? 'bg-muted'
                      : 'hover:bg-muted'
                  }`}
                >
                  <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-primary-foreground text-xs font-medium">
                      {getUserInitials()}
                    </span>
                  </div>
                  <span className="text-sm font-medium">
                    {user.name || user.email?.split('@')[0] || 'User'}
                  </span>
                </button>

                {/* Dropdown Menu */}
                {showDesktopDropdown && (
                  <div className="w-72 bg-card rounded-lg shadow-lg border border-border z-50 absolute right-0 mt-2 animate-in fade-in-0 zoom-in-95 duration-200">
                    {/* User Info Header */}
                    <div className="font-normal p-4">
                      <div className="flex flex-col space-y-2">
                        <p className="text-sm font-medium leading-none">
                          {user.name || 'User'}
                        </p>
                        <p className="text-xs leading-none text-muted-foreground">
                          {user.email || 'user@example.com'}
                        </p>
                      </div>
                    </div>

                    <hr className="border-border" />

                    {/* Profile & Settings */}
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
                        <Settings className="mr-2 h-4 w-4" />
                        <span>Settings</span>
                      </button>
                    </div>

                    <hr className="border-border" />
                     <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleTheme}
                  className="rounded-full"
                >
                  {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </Button>
                    <div className="p-1">
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-2 py-2 text-sm hover:bg-accent rounded-sm transition-colors duration-200 text-foreground"
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Log out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
                whileHover={{ scale: 1.05 }}
              >
                <a
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-full hover:bg-primary/90 transition-colors"
                >
                  Sign In
                </a>
              </motion.div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <motion.button className="md:hidden flex items-center" onClick={toggleMenu} whileTap={{ scale: 0.9 }}>
            <Menu className="h-6 w-6 text-foreground" />
          </motion.button>
        </div>

        {/* Mobile Menu Overlay */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              className="fixed inset-0 bg-background z-50 pt-24 px-6 md:hidden"
              initial={{ opacity: 0, x: "100%" }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
            >
              <div className="flex items-center gap-4">
                {user && (
                  <>
                    <Button
                      variant="ghost"
                      onClick={() => navigate('/home')}
                      className="flex items-center gap-2"
                    >
                      <Home className="h-4 w-4" />
                      Home
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={() => navigate('/ai-test')}
                      className="flex items-center gap-2"
                    >
                      <Sparkles className="h-4 w-4" />
                      AI Test
                    </Button>
                  </>
                )}
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleTheme}
                  className="rounded-full"
                >
                  {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                  <span>Theme</span>
                </Button>
              </div>
              {/* <div className="flex flex-col space-y-6">
                {["Home", "Features", "Pricing", "Documentation"].map((item, i) => (
                  <motion.div
                    key={item}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 + 0.1 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <a 
                      href={item === "Home" ? "/" : item === "Features" ? "/#features" : item === "Pricing" ? "/#pricing" : "/docs"}
                      className="text-base text-foreground font-medium" 
                      onClick={toggleMenu}
                    >
                      {item}
                    </a>
                  </motion.div>
                ))}

                <div className="flex items-center justify-between pt-6">
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
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        handleLogout();
                        toggleMenu();
                      }}
                      className="rounded-full"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Logout
                    </Button>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 }}
                      exit={{ opacity: 0, y: 20 }}
                    >
                      <a
                        href="/login"
                        className="inline-flex items-center justify-center px-5 py-2 text-base text-primary-foreground bg-primary rounded-full hover:bg-muted transition-colors"
                        onClick={toggleMenu}
                      >
                        Get Started
                      </a>
                    </motion.div>
                  )}
                </div>
              </div> */}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* Profile Modal */}
      <ProfileModal 
        open={showProfileModal} 
        onOpenChange={setShowProfileModal} 
      />
      
      {/* Settings Modal */}
      <SettingsModal 
        open={showSettingsModal} 
        onOpenChange={setShowSettingsModal} 
      />
    </>
  )
}

export { TopBar }