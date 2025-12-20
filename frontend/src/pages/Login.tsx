import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { SiGoogle } from "react-icons/si";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

export default function Login() {
  const navigate = useNavigate();
  const { user, isLoading, login } = useAuth();
  const { toast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 🔁 If already logged in, go to home
  useEffect(() => {
    if (!isLoading && user) {
      navigate("/home", { replace: true });
    }
  }, [user, isLoading, navigate]);

  const handleGoogleLogin = () => {
    window.location.href = "http://localhost:6001/auth/google";
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please enter both email and password.",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      await login(email, password);
      toast({
        title: "Success",
        description: "Logged in successfully.",
      });
      // Navigation is handled by the useEffect above when user state updates
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Login Failed",
        description: error.message || "Invalid credentials.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Checking authentication...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-8 ">
        <div className="bg-card border border-border rounded-2xl p-8 space-y-6">
          <div className="text-center">
            <h2 className="text-4xl font-bold tracking-tight">Welcome Back</h2>
            <p className="text-xl text-muted-foreground mt-2">
              Sign in to your account
            </p>
          </div>

        

          

          {/* Email/Password Form */}
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="rounded-xl"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-primary hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="rounded-xl"
              />
            </div>

            <Button 
              type="submit" 
              className="w-full h-12 rounded-xl" 
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign In"}
            </Button>

            {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Or continue with email
              </span>
            </div>
          </div>

            {/* Google Login */}
          <Button
            type="button"
            variant="outline"
            onClick={handleGoogleLogin}
            className="w-full h-12 rounded-xl"
            data-testid="button-google"
          >
            <SiGoogle className="mr-2 h-4 w-4" />
            Continue with Google
          </Button>
          </form>

          {/* Sign Up Link */}
          <div className="text-center text-sm">
            <p className="text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link 
                to="/signup" 
                className="font-semibold text-primary hover:underline"
              >
                Sign up
              </Link>
            </p>
          </div>
          
          <p className="text-center text-xs text-muted-foreground pt-4">
            By continuing, you agree to our Terms & Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}