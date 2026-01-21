import { useState } from "react";
import {
  Zap,
  User,
  CreditCard,
  ArrowLeft,
  Camera,
  Mail,
  Calendar,
  Shield,
  Key,
  Bell,
  Sparkles,
  Check,
  Youtube,
  Instagram,
  Globe,
  Crown,
  TrendingUp,
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Separator } from "./ui/separator";
import Navbar from "./Navbar";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import mockUserData from "../data/userData.json"; // Mock data for unimplemented features

export function Profile() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Use real user data for profile, mock data for unimplemented features
  const userData = mockUserData;
  
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [weeklyReports, setWeeklyReports] = useState(true);

  // Helper function to get user initials
  const getInitials = (name, email) => {
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    if (email) {
      return email.substring(0, 2).toUpperCase();
    }
    return 'U';
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  const iconMap = {
    Youtube,
    Instagram,
    Globe,
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <Navbar
        variant="profile"
        onNavigate={(page) => navigate(`/${page}`)}
        userData={user}
        backTarget="Dashboard"
      />

      <br />
      <br />
      {/* Main Content */}
      <main className="container mx-auto px-3 max-w-7xl bg-white">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Profile Settings</h1>
          <p className="text-gray-600">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Profile Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Card */}
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your personal information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Profile Picture */}
                <div className="flex items-center gap-6">
                  <div className="relative">
                    <Avatar className="size-24">
                      <AvatarImage src={user?.avatar} alt={user?.username} />
                      <AvatarFallback className="bg-gradient-to-br from-purple-600 to-blue-600 text-white text-2xl">
                        {getInitials(user?.username, user?.email)}
                      </AvatarFallback>
                    </Avatar>
                    <Button
                      size="sm"
                      className="absolute -bottom-2 -right-2 rounded-full size-8 p-0 bg-gradient-to-r from-purple-600 to-blue-600"
                    >
                      <Camera className="size-4" />
                    </Button>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-1">Profile Photo</p>
                    <p className="text-xs text-gray-500 mb-2">
                      PNG, JPG up to 5MB
                    </p>
                    <Button variant="outline" size="sm">
                      Upload New Photo
                    </Button>
                  </div>
                </div>

                <Separator />

                {/* Name */}
                <div className="space-y-2">
                  <Label htmlFor="name">Username</Label>
                  <Input id="name" className="border border-gray-300 rounded-md bg-gray-100" defaultValue={user?.username} />
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    className="border border-gray-300 rounded-md bg-gray-100"
                    defaultValue={user?.email}
                  />
                </div>

                {/* Member Since */}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="size-4" />
                  <span>Member since {formatDate(user?.created_at)}</span>
                </div>

                <Button className="bg-gradient-to-r from-purple-600 to-blue-600">
                  Save Changes
                </Button>
              </CardContent>
            </Card>

            {/* Security Card */}
            <Card>
              <CardHeader>
                <CardTitle>Security</CardTitle>
                <CardDescription>
                  Manage your password and security settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current-password">Current Password</Label>
                  <Input
                    id="current-password"
                    className="border border-gray-300 rounded-md bg-gray-100"
                    type="password"
                    placeholder="••••••••"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <Input
                    id="new-password"
                    className="border border-gray-300 rounded-md bg-gray-100"
                    type="password"
                    placeholder="••••••••"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm-password">Confirm New Password</Label>
                  <Input
                    id="confirm-password"
                    className="border border-gray-300 rounded-md bg-gray-100"
                    type="password"
                    placeholder="••••••••"
                  />
                </div>
                <Button variant="outline">
                  <Shield className="size-4 mr-2" />
                  Update Password
                </Button>
              </CardContent>
            </Card>

            {/* API Keys Card */}
            <Card>
              <CardHeader>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>
                  Manage API keys for integrations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap items-center justify-between p-4 gap-2 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Key className="size-5 text-gray-600" />
                    <div>
                      <p className="text-sm font-medium">Production API Key</p>
                      <p className="text-xs text-gray-500 font-mono">
                        ff_prod_••••••••••••4a8c
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="bg-white">
                    Regenerate
                  </Button>
                </div>
                <div className="flex flex-wrap items-center justify-between p-4 gap-2 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Key className="size-5 text-gray-600" />
                    <div>
                      <p className="text-sm font-medium">Development API Key</p>
                      <p className="text-xs text-gray-500 font-mono">
                        ff_dev_••••••••••••7b2f
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="bg-white">
                    Regenerate
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Notifications Card */}
            <Card>
              <CardHeader>
                <CardTitle>Notifications</CardTitle>
                <CardDescription>
                  Manage how you receive updates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Mail className="size-5 text-gray-600" />
                    <div>
                      <p className="text-sm font-medium">Email Notifications</p>
                      <p className="text-xs text-gray-500">
                        Receive email updates about your pipelines
                      </p>
                    </div>
                  </div>
                  <Switch
                    checked={emailNotifications}
                    onCheckedChange={setEmailNotifications}
                  />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bell className="size-5 text-gray-600" />
                    <div>
                      <p className="text-sm font-medium">Push Notifications</p>
                      <p className="text-xs text-gray-500">
                        Get alerts for important events
                      </p>
                    </div>
                  </div>
                  <Switch
                    checked={pushNotifications}
                    onCheckedChange={setPushNotifications}
                  />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <TrendingUp className="size-5 text-gray-600" />
                    <div>
                      <p className="text-sm font-medium">Weekly Reports</p>
                      <p className="text-xs text-gray-500">
                        Summary of your content performance
                      </p>
                    </div>
                  </div>
                  <Switch
                    checked={weeklyReports}
                    onCheckedChange={setWeeklyReports}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Subscription & Stats */}
          <div className="space-y-6">
            {/* Subscription Card */}
            <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Crown className="size-5 text-purple-600" />
                    Subscription
                  </CardTitle>
                  <Badge className="bg-green-100 text-green-700 border-green-200">
                    {userData.subscription.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-2xl font-bold text-purple-600">
                    {userData.subscription.plan}
                  </p>
                  <p className="text-sm text-gray-600">
                    {userData.subscription.price}
                  </p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Started:</span>
                    <span className="font-medium">
                      {new Date(
                        userData.subscription.startDate,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Renews:</span>
                    <span className="font-medium">
                      {new Date(
                        userData.subscription.endDate,
                      ).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <p className="text-sm font-medium mb-2">Plan Features:</p>
                  {userData.subscription.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <Check className="size-4 text-purple-600" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2 pt-2">
                  <Button className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600">
                    <Sparkles className="size-4 mr-2" />
                    Upgrade
                  </Button>
                  <Button variant="outline" className="flex-1">
                    Manage
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Usage Stats Card */}
            <Card>
              <CardHeader>
                <CardTitle>Usage Statistics</CardTitle>
                <CardDescription>Your activity this month</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Pipelines</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {userData.usage.pipelinesCreated}
                      </p>
                    </div>
                    <Zap className="size-8 text-purple-600" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Content Generated</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {userData.usage.contentGenerated}
                      </p>
                    </div>
                    <Sparkles className="size-8 text-blue-600" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Total Views</p>
                      <p className="text-2xl font-bold text-green-600">
                        {userData.usage.totalViews}
                      </p>
                    </div>
                    <TrendingUp className="size-8 text-green-600" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Engagement</p>
                      <p className="text-2xl font-bold text-orange-600">
                        {userData.usage.totalEngagement}
                      </p>
                    </div>
                    <TrendingUp className="size-8 text-orange-600" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Connected Platforms Card */}
            <Card>
              <CardHeader>
                <CardTitle>Connected Platforms</CardTitle>
                <CardDescription>
                  Manage your platform integrations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {userData.connectedPlatforms.map((platform, idx) => {
                  const Icon = iconMap[platform.icon];
                  return (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="size-10 bg-white rounded-lg border flex items-center justify-center">
                          {Icon && <Icon className="size-5 text-gray-700" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{platform.name}</p>
                          <p className="text-xs text-gray-500">
                            {platform.connected
                              ? `${platform.accounts} account${platform.accounts > 1 ? "s" : ""}`
                              : "Not connected"}
                          </p>
                        </div>
                      </div>

                      {platform.connected ? (
                        <Badge
                          variant="outline"
                          className="bg-green-50 text-green-700 border-green-200"
                        >
                          Connected
                        </Badge>
                      ) : (
                        <Button size="sm" variant="outline">
                          Connect
                        </Button>
                      )}
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
