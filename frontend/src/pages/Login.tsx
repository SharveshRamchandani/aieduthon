import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

import { SiGoogle } from "react-icons/si";
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { TopBar } from '@/components/TopBar';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login:", { email, password, rememberMe });
    
    try {
      await login(email, password);
      navigate("/home");
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to login',
        variant: 'destructive',
      });
    }
  };

  const handleGoogleLogin = () => {
    console.log("Google login");
    //todo: remove mock functionality
    alert("Google login will be implemented");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 pt-32">
      <TopBar />
      <div className="w-full max-w-md space-y-8">
         
         <div className="bg-card border border-border rounded-2xl p-8 space-y-6"> <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight">Welcome</h2>
          <p className="text-muted-foreground mt-2">Login to your account</p>
        </div>
      <form onSubmit={handleLogin} className="space-y-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="h-12 rounded-xl"
              data-testid="input-email"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="h-12 rounded-xl"
              data-testid="input-password"
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Checkbox
              id="remember"
              checked={rememberMe}
              onCheckedChange={(checked) => setRememberMe(checked === true)}
              data-testid="checkbox-remember"
            />
            <Label htmlFor="remember" className="text-sm font-normal cursor-pointer">
              Keep me signed in
            </Label>
          </div>
          <button
            type="button"
            className="text-sm text-primary hover:underline"
            data-testid="button-reset-password"
          >
            Reset password
          </button>
        </div>

        <Button
          type="submit"
          className="w-full h-12 rounded-xl font-semibold"
          data-testid="button-signin"
        >
          Sign In
        </Button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
          </div>
        </div>

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

        <p className="text-center text-sm text-muted-foreground">
          New to our platform?{" "}
          <button
            type="button"
            onClick={() => navigate("/signup")}
            className="text-primary hover:underline font-medium"
            data-testid="button-create-account"
          >
            Create Account
          </button>
        </p>
      </form>
      </div>
      </div>
   </div>
  );
}