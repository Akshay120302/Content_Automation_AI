import { useState } from 'react';
import { 
  Zap, 
  CreditCard,
  ArrowLeft,
  Check,
  Shield,
  Lock,
  ChevronDown,
  Info
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { useAuth } from '../contexts/AuthContext';
import Navbar from './Navbar';

export function SubscriptionPage({ onNavigate, selectedPlan = 'Pro' }) {
  const { user } = useAuth();
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  const plans = {
    Starter: {
      name: 'Starter',
      monthlyPrice: 499,
      yearlyPrice: 4990,
      features: [
        '1–2 Pipelines',
        'Text & Image Content',
        'Basic Analytics',
        'Email Support',
        'Auto Publishing'
      ]
    },
    Pro: {
      name: 'Pro',
      monthlyPrice: 1499,
      yearlyPrice: 14990,
      features: [
        '3–4 Pipelines',
        'Limited Video Generation',
        'All Content Types',
        'Advanced Analytics',
        'Priority Email Support',
        'API Access'
      ]
    },
    Studio: {
      name: 'Studio',
      monthlyPrice: 2999,
      yearlyPrice: 29990,
      features: [
        '5–10 Pipelines',
        'Full Video Generation',
        'All Content Types',
        'Premium Analytics',
        'Priority Support',
        'API Access',
        'Custom Branding'
      ]
    }
  };

  const currentPlan = plans[selectedPlan] || plans.Pro;
  const price = billingCycle === 'monthly' ? currentPlan.monthlyPrice : currentPlan.yearlyPrice;
  const savings = billingCycle === 'yearly' ? (currentPlan.monthlyPrice * 12 - currentPlan.yearlyPrice) : 0;
  const gst = Math.round(price * 0.18);
  const total = price + gst;

  const handleSubscribe = () => {
    if (!acceptedTerms) {
      alert('Please accept the terms and conditions');
      return;
    }
    // Here you would integrate with payment gateway
    alert('Payment processing... (This is a demo)');
    setTimeout(() => {
      onNavigate('dashboard');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <Navbar variant="profile" onNavigate={onNavigate} userData={user} backTarget="dashboard" />

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold mb-2">Complete Your Subscription</h1>
          <p className="text-gray-600">Start your 14-day free trial today. Cancel anytime.</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Payment Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Plan Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Select Your Plan</CardTitle>
                <CardDescription>Choose the plan that works best for you</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select defaultValue={selectedPlan} onValueChange={(value) => onNavigate('subscription')}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a plan" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Starter">Starter - ₹499/month</SelectItem>
                    <SelectItem value="Pro">Pro - ₹1,499/month</SelectItem>
                    <SelectItem value="Studio">Studio - ₹2,999/month</SelectItem>
                  </SelectContent>
                </Select>

                {/* Billing Cycle */}
                <div className="space-y-3">
                  <Label>Billing Cycle</Label>
                  <RadioGroup value={billingCycle} onValueChange={setBillingCycle}>
                    <div className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <div className="flex items-center gap-3">
                        <RadioGroupItem value="monthly" id="monthly" />
                        <Label htmlFor="monthly" className="cursor-pointer">
                          <div>
                            <p className="font-medium">Monthly</p>
                            <p className="text-sm text-gray-500">₹{currentPlan.monthlyPrice}/month</p>
                          </div>
                        </Label>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50 relative">
                      <div className="flex items-center gap-3">
                        <RadioGroupItem value="yearly" id="yearly" />
                        <Label htmlFor="yearly" className="cursor-pointer">
                          <div>
                            <p className="font-medium">Yearly</p>
                            <p className="text-sm text-gray-500">₹{currentPlan.yearlyPrice}/year</p>
                          </div>
                        </Label>
                      </div>
                      <Badge className="bg-green-100 text-green-700 border-green-200">
                        Save ₹{currentPlan.monthlyPrice * 12 - currentPlan.yearlyPrice}
                      </Badge>
                    </div>
                  </RadioGroup>
                </div>
              </CardContent>
            </Card>

            {/* Payment Method */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Method</CardTitle>
                <CardDescription>Select your preferred payment method</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
                  <div className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="card" id="card" />
                    <Label htmlFor="card" className="cursor-pointer flex items-center gap-2 flex-1">
                      <CreditCard className="size-5 text-gray-600" />
                      <span>Credit / Debit Card</span>
                    </Label>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="upi" id="upi" />
                    <Label htmlFor="upi" className="cursor-pointer flex items-center gap-2 flex-1">
                      <div className="size-5 bg-gradient-to-r from-purple-600 to-orange-600 rounded" />
                      <span>UPI</span>
                    </Label>
                  </div>
                  <div className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="netbanking" id="netbanking" />
                    <Label htmlFor="netbanking" className="cursor-pointer flex items-center gap-2 flex-1">
                      <div className="size-5 bg-blue-600 rounded" />
                      <span>Net Banking</span>
                    </Label>
                  </div>
                </RadioGroup>

                {/* Card Details */}
                {paymentMethod === 'card' && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="space-y-2">
                      <Label htmlFor="cardNumber">Card Number</Label>
                      <Input id="cardNumber" placeholder="1234 5678 9012 3456" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="expiry">Expiry Date</Label>
                        <Input id="expiry" placeholder="MM/YY" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="cvv">CVV</Label>
                        <Input id="cvv" placeholder="123" maxLength={3} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="cardName">Cardholder Name</Label>
                      <Input id="cardName" placeholder="John Doe" />
                    </div>
                  </div>
                )}

                {/* UPI Details */}
                {paymentMethod === 'upi' && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="space-y-2">
                      <Label htmlFor="upiId">UPI ID</Label>
                      <Input id="upiId" placeholder="yourname@upi" />
                    </div>
                  </div>
                )}

                {/* Net Banking */}
                {paymentMethod === 'netbanking' && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="space-y-2">
                      <Label htmlFor="bank">Select Bank</Label>
                      <Select>
                        <SelectTrigger id="bank">
                          <SelectValue placeholder="Choose your bank" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="hdfc">HDFC Bank</SelectItem>
                          <SelectItem value="icici">ICICI Bank</SelectItem>
                          <SelectItem value="sbi">State Bank of India</SelectItem>
                          <SelectItem value="axis">Axis Bank</SelectItem>
                          <SelectItem value="kotak">Kotak Mahindra Bank</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Billing Information */}
            <Card>
              <CardHeader>
                <CardTitle>Billing Information</CardTitle>
                <CardDescription>Enter your billing details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input id="firstName" placeholder="John" defaultValue={user?.username?.split(' ')[0] || ''} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input id="lastName" placeholder="Doe" defaultValue={user?.username?.split(' ')[1] || ''} />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" placeholder="john@example.com" defaultValue={user?.email || ''} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input id="phone" placeholder="+91 98765 43210" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input id="address" placeholder="123 Street Name" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input id="city" placeholder="Mumbai" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pincode">Pin Code</Label>
                    <Input id="pincode" placeholder="400001" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State</Label>
                  <Select>
                    <SelectTrigger id="state">
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="maharashtra">Maharashtra</SelectItem>
                      <SelectItem value="delhi">Delhi</SelectItem>
                      <SelectItem value="karnataka">Karnataka</SelectItem>
                      <SelectItem value="tamil-nadu">Tamil Nadu</SelectItem>
                      <SelectItem value="gujarat">Gujarat</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Terms and Conditions */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="terms"
                    checked={acceptedTerms}
                    onChange={(e) => setAcceptedTerms(e.target.checked)}
                    className="mt-1"
                  />
                  <Label htmlFor="terms" className="text-sm cursor-pointer">
                    I agree to the{' '}
                    <a href="#" className="text-purple-600 hover:underline">Terms of Service</a>
                    {' '}and{' '}
                    <a href="#" className="text-purple-600 hover:underline">Privacy Policy</a>.
                    I understand that my subscription will automatically renew unless cancelled.
                  </Label>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Order Summary */}
          <div>
            <div className="sticky top-24">
              <Card className="border-2">
                <CardHeader className="bg-gradient-to-br from-purple-50 to-blue-50">
                  <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 pt-6">
                  {/* Plan Details */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-lg">{currentPlan.name} Plan</span>
                      <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
                        {billingCycle === 'monthly' ? 'Monthly' : 'Yearly'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">
                      {billingCycle === 'monthly' ? 'Billed monthly' : 'Billed annually'}
                    </p>

                    {/* Features */}
                    <div className="space-y-2 mb-4">
                      {currentPlan.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <Check className="size-4 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Trial Info */}
                  <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                    <Info className="size-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-blue-900">
                      Your 14-day free trial starts today. You won't be charged until {new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toLocaleDateString()}.
                    </p>
                  </div>

                  <Separator />

                  {/* Price Breakdown */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Subtotal</span>
                      <span className="font-medium">₹{price.toLocaleString()}</span>
                    </div>
                    {savings > 0 && (
                      <div className="flex items-center justify-between text-green-600">
                        <span>Yearly Savings</span>
                        <span className="font-medium">-₹{savings.toLocaleString()}</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">GST (18%)</span>
                      <span className="font-medium">₹{gst.toLocaleString()}</span>
                    </div>
                  </div>

                  <Separator />

                  {/* Total */}
                  <div className="flex items-center justify-between text-lg">
                    <span className="font-bold">Total</span>
                    <span className="font-bold text-purple-600">₹{total.toLocaleString()}</span>
                  </div>

                  {/* Subscribe Button */}
                  <Button 
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    size="lg"
                    onClick={handleSubscribe}
                    disabled={!acceptedTerms}
                  >
                    <Lock className="size-4 mr-2" />
                    Start Free Trial
                  </Button>

                  {/* Security Badge */}
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500 pt-2">
                    <Shield className="size-4 text-green-600" />
                    <span>Secured by 256-bit SSL encryption</span>
                  </div>

                  {/* Money Back Guarantee */}
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600">
                      💯 <strong>30-Day Money Back Guarantee</strong>
                      <br />
                      Cancel anytime, no questions asked
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
