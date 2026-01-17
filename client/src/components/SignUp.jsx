import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Lock, User, Github, Chrome, Sparkles, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Checkbox } from './ui/checkbox';


export function SignUp() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle sign up logic here
    console.log('Sign up with:', formData);
  };

  const features = [
    'Unlimited workflow executions',
    'Access to all AI models',
    'Multi-platform publishing',
    '24/7 customer support'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center p-6">
      <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left side - Benefits */}
        <div className="hidden md:block">
          <div className="flex items-center gap-2 mb-6">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
              <Sparkles className="size-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              FlowForge
            </span>
          </div>

          <h2 className="text-4xl font-bold mb-4 text-gray-700">
            Start forging your workflows today
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of creators automating their content creation with AI
          </p>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                  <Check className="size-4 text-white" />
                </div>
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>

          <div className="mt-8 p-6 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl">
            <p className="text-sm text-gray-700 italic">
              "FlowForge transformed how I create content. What used to take hours now happens automatically while I sleep!"
            </p>
            <p className="text-sm font-semibold mt-2 text-gray-700">— Sarah Chen, Content Creator</p>
          </div>
        </div>

        {/* Right side - Sign up form */}
        <div className="w-full">
          <Button 
            variant="ghost" 
            className="mb-6 md:hidden"
            onClick={() => navigate('/signup')}
          >
            <ArrowLeft className="size-4 mr-2 text-black" />
            Back to home
          </Button>

          <div className="bg-white rounded-2xl shadow-xl p-8 border-2">
            {/* Mobile logo */}
            <div className="flex items-center gap-2 mb-6 justify-center md:hidden">
              <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
                <Sparkles className="size-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                FlowForge
              </span>
            </div>

            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold mb-2 text-black">Create your account</h1>
              <p className="text-gray-600">Start building AI workflows for free</p>
            </div>

            {/* Social signup buttons */}
            <div className="space-y-3 mb-6">
              <Button variant="outline" className="w-full text-gray-700">
                <Chrome className="size-5 mr-2" />
                Sign up with Google
              </Button>
              <Button variant="outline" className="w-full text-gray-700">
                <Github className="size-5 mr-2" />
                Sign up with GitHub
              </Button>
            </div>

            <div className="relative mb-6">
              <Separator />
              <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-3 text-sm text-gray-500">
                or sign up with email
              </span>
            </div>

            {/* Sign up form */}
            <form onSubmit={handleSubmit} className="space-y-4 text-gray-700">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="signup-email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="signup-password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-gray-400" />
                  <Input
                    id="confirm-password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="flex items-start gap-2">
                <Checkbox 
                  id="terms"
                  checked={formData.agreeToTerms}
                  onCheckedChange={(checked) => 
                    setFormData({...formData, agreeToTerms: Boolean(checked)})
                  }
                  required
                />
                <label htmlFor="terms" className="text-sm text-gray-600 leading-relaxed">
                  I agree to the{' '}
                  <a href="#" className="text-purple-600 hover:underline">Terms of Service</a>
                  {' '}and{' '}
                  <a href="#" className="text-purple-600 hover:underline">Privacy Policy</a>
                </label>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600" 
                size="lg"
              >
                Create account
              </Button>
            </form>

            <p className="text-center text-sm text-gray-600 mt-6">
              Already have an account?{' '}
              <button 
                onClick={() => navigate('/signin')}
                className="text-purple-600 hover:text-purple-700 font-semibold"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
