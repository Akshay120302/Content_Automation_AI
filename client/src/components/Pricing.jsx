import { Check, X, Zap, Crown, Rocket, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function Pricing({ onNavigate }) {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = (planName) => {
    if (isAuthenticated) {
      // Redirect to subscription page with selected plan
      navigate(`/subscription?plan=${planName}`);
    } else {
      // Redirect to signin page
      navigate('/signin');
    }
  };
  const plans = [
    {
      name: 'Starter',
      price: '₹499',
      period: '/month',
      description: 'Perfect for individuals getting started',
      icon: Zap,
      popular: false,
      features: [
        { name: '1–2 Pipelines', included: true },
        { name: 'Video Generation', included: false },
        { name: 'Text & Image Content', included: true },
        { name: 'Basic Analytics', included: true },
        { name: 'Email Support', included: true },
        { name: 'Auto Publishing', included: true },
        { name: 'Priority Support', included: false },
        { name: 'Custom Branding', included: false },
      ],
      gradient: 'from-gray-600 to-gray-700',
      bgGradient: 'from-gray-50 to-gray-100',
    },
    {
      name: 'Pro',
      price: '₹1,499',
      period: '/month',
      description: 'Best for growing content creators',
      icon: Crown,
      popular: true,
      features: [
        { name: '3–4 Pipelines', included: true },
        { name: 'Limited Video Generation', included: true, highlight: true },
        { name: 'All Content Types', included: true },
        { name: 'Advanced Analytics', included: true },
        { name: 'Priority Email Support', included: true },
        { name: 'Auto Publishing', included: true },
        { name: 'API Access', included: true },
        { name: 'Custom Branding', included: false },
      ],
      gradient: 'from-purple-600 to-blue-600',
      bgGradient: 'from-purple-50 to-blue-50',
    },
    {
      name: 'Studio',
      price: '₹2,999',
      period: '/month',
      description: 'For professional teams and agencies',
      icon: Rocket,
      popular: false,
      features: [
        { name: '5–10 Pipelines', included: true },
        { name: 'Full Video Generation', included: true, highlight: true },
        { name: 'All Content Types', included: true },
        { name: 'Premium Analytics', included: true },
        { name: 'Priority Support', included: true },
        { name: 'Auto Publishing', included: true },
        { name: 'API Access', included: true },
        { name: 'Custom Branding', included: true },
      ],
      gradient: 'from-orange-600 to-red-600',
      bgGradient: 'from-orange-50 to-red-50',
    },
  ];

  return (
    <section id="pricing" className="py-24 px-6 bg-white">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
            Pricing Plans
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Choose Your Perfect Plan
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Start free and scale as you grow. All plans include core automation features.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            return (
              <Card
                key={index}
                className={`relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:scale-105 ${
                  plan.popular
                    ? 'border-2 border-purple-500 shadow-xl'
                    : 'border-2 border-gray-200'
                }`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute top-0 right-0">
                    <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-1 text-xs font-semibold rounded-bl-lg">
                      MOST POPULAR
                    </div>
                  </div>
                )}

                <CardHeader className={`pb-8 bg-gradient-to-br ${plan.bgGradient}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-lg bg-gradient-to-br ${plan.gradient}`}>
                      <Icon className="size-6 text-white" />
                    </div>
                  </div>
                  <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
                  <CardDescription className="text-sm">
                    {plan.description}
                  </CardDescription>
                  <div className="mt-6">
                    <div className="flex items-baseline">
                      <span className="text-5xl font-bold">{plan.price}</span>
                      <span className="text-gray-600 ml-2">{plan.period}</span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-6">
                  {/* Features List */}
                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-3">
                        {feature.included ? (
                          <div className={`flex-shrink-0 rounded-full p-1 ${
                            plan.popular
                              ? 'bg-gradient-to-r from-purple-600 to-blue-600'
                              : 'bg-green-500'
                          }`}>
                            <Check className="size-3 text-white" />
                          </div>
                        ) : (
                          <div className="flex-shrink-0 rounded-full p-1 bg-gray-300">
                            <X className="size-3 text-gray-600" />
                          </div>
                        )}
                        <span
                          className={`text-sm ${
                            feature.included ? 'text-gray-700' : 'text-gray-400'
                          } ${feature.highlight ? 'font-semibold' : ''}`}
                        >
                          {feature.name}
                        </span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <Button
                    onClick={() => handleGetStarted(plan.name)}
                    className={`w-full ${
                      plan.popular
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white'
                        : 'bg-gray-900 hover:bg-gray-800 text-white'
                    }`}
                  >
                    {plan.popular && <Sparkles className="size-4 mr-2 text-white" />}
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-4">
            All plans include 14-day free trial. No credit card required.
          </p>
          <div className="flex items-center justify-center gap-8 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Check className="size-4 text-green-600" />
              <span>Cancel anytime</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="size-4 text-green-600" />
              <span>Secure payment</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="size-4 text-green-600" />
              <span>24/7 support</span>
            </div>
          </div>
        </div>

        {/* Enterprise Section */}
        <div className="mt-16">
          <Card className="bg-gradient-to-br from-gray-900 to-gray-800 text-white border-0">
            <CardContent className="p-8 md:p-12">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                  <h3 className="text-2xl font-bold mb-2">Need a Custom Solution?</h3>
                  <p className="text-gray-300">
                    Get unlimited pipelines, dedicated support, and custom AI models for your enterprise.
                  </p>
                </div>
                <Button
                  variant="outline"
                  className="bg-white text-gray-900 hover:bg-gray-100 border-0 whitespace-nowrap"
                  onClick={() => {
                    if (isAuthenticated) {
                      navigate('/subscription?plan=Enterprise');
                    } else {
                      navigate('/signin');
                    }
                  }}
                >
                  Contact Sales
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
