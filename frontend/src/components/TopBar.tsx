import { Moon, Sun, LogOut, User } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export const TopBar = () => {
  const { isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="text-xl font-bold tracking-tight">SlideGen</div>
        
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="rounded-full"
          >
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          
          {user && (
            <>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-border">
                <User className="h-4 w-4" />
                <span className="text-sm font-medium">{user.name}</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="rounded-full"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
