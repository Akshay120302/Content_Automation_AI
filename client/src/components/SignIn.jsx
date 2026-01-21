import { useState } from "react";
import { ArrowLeft, Mail, Lock, Github, Chrome, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Separator } from "./ui/separator";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../hooks/use-toast";


export function SignIn() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const { toast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setIsLoading(true);

    try {
      await login({ email, password });

      toast({
        title: "Success!",
        description: "Welcome back!",
      });

      // Redirect to dashboard
      navigate("/dashboard");
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Invalid email or password",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Back button */}
        {/* <Button 
          variant="ghost" 
          className="mb-6"
          onClick={() => navigate('/')}
        >
          <ArrowLeft className="size-4 mr-2 text-black" />
          <span className="text-black">Back to home</span>
        </Button> */}

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border-2">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-8 justify-center">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
              <Sparkles className="size-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              FlowForge
            </span>
          </div>

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2 text-black">Welcome back</h1>
            <p className="text-gray-600">Sign in to continue building your workflows</p>
          </div>

          {/* Social login buttons */}
          <div className="space-y-3 mb-6">
            <Button variant="outline" className="w-full text-black" size="lg">
              <Chrome className="size-5 mr-2 text-black" />
              Continue with Google
            </Button>
            <Button variant="outline" className="w-full text-black" size="lg">
              <Github className="size-5 mr-2" />
              Continue with GitHub
            </Button>
          </div>

          <div className="relative mb-6">
            <Separator />
            <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-3 text-sm text-gray-700">
              or continue with email
            </span>
          </div>

          {/* Sign in form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2 text-gray-700">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-gray-700">
                <Label htmlFor="password">Password</Label>
                <a href="#" className="text-sm text-purple-600 hover:text-purple-700">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600" 
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Don't have an account?{' '}
            <button 
              onClick={() => navigate('/signup')}
              className="text-purple-600 hover:text-purple-700 font-semibold"
            >
              Sign up
            </button>
          </p>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          By signing in, you agree to our{' '}
          <a href="#" className="text-purple-600 hover:underline">Terms of Service</a>
          {' '}and{' '}
          <a href="#" className="text-purple-600 hover:underline">Privacy Policy</a>
        </p>
      </div>
    </div>
  );
}