import { useState } from "react";
import {
  Zap,
  User,
  CreditCard,
  Play,
  Pause,
  CheckCircle2,
  Clock,
  TrendingUp,
  Eye,
  ThumbsUp,
  MessageCircle,
  Activity,
  Info,
  AlertTriangle,
  XCircle,
  ArrowLeft,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { useNavigate } from "react-router-dom";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { ScrollArea } from "./ui/scroll-area";
import sampleData from "../data/pipeline-sample-data.json";
import Navbar from "./Navbar";
import userData from "../data/userData.json";

export function PipelineDetailsView({ pipelineId }) {
      const navigate = useNavigate();
  const [pipelineStatus, setPipelineStatus] = useState("active");
  const [data] = useState(sampleData);

  const toggleStatus = () => {
    setPipelineStatus((prev) => (prev === "active" ? "paused" : "active"));
  };

  const getLogIcon = (type) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="size-4 text-green-600" />;
      case "error":
        return <XCircle className="size-4 text-red-600" />;
      case "warning":
        return <AlertTriangle className="size-4 text-yellow-600" />;
      case "info":
      default:
        return <Info className="size-4 text-blue-600" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <Navbar
        variant="profile"
        onNavigate={(page) => navigate(`/${page}`)}
        userData={userData}
        backTarget="dashboard"
      />

 
      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr_320px] gap-6">
          {/* Left Sidebar - Pipeline Status */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Activity className="size-5" />
                  Pipeline Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Active/Pause Toggle */}
                <div className="space-y-2">
                  <Button
                    onClick={toggleStatus}
                    className={`w-full ${
                      pipelineStatus === 'active'
                        ? 'bg-green-600 hover:bg-green-700'
                        : 'bg-gray-400 hover:bg-gray-500'
                    }`}
                  >
                    {pipelineStatus === 'active' ? (
                      <>
                        <Play className="size-4 mr-2" fill="currentColor" />
                        Active
                      </>
                    ) : (
                      <>
                        <Pause className="size-4 mr-2" />
                        Paused
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={toggleStatus}
                  >
                    {pipelineStatus === 'active' ? (
                      <>
                        <Pause className="size-4 mr-2" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="size-4 mr-2" />
                        Resume
                      </>
                    )}
                  </Button>
                </div>

                {/* Configuration Items */}
                <div className="space-y-3 pt-4 border-t">
                  {data.pipelineStatus.configurations.map((config) => (
                    <div key={config.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                      <div className="size-8 bg-white rounded border flex items-center justify-center">
                        <CheckCircle2 className="size-4 text-green-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{config.label}</p>
                        <p className="text-xs text-gray-500">{config.value}</p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 pt-4 border-t">
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <p className="text-xs text-gray-600">Total Posts</p>
                    <p className="text-xl font-bold text-purple-600">{data.pipelineStatus.totalPosts}</p>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-gray-600">Success Rate</p>
                    <p className="text-xl font-bold text-blue-600">{data.pipelineStatus.successRate}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center Content - Tabs */}
          <div>
            <Tabs defaultValue="queue" className="w-full">
              {/* <TabsList className="w-full grid grid-cols-3 mb-4"> */}
              <TabsList className="w-full flex items-center gap-2 p-1.5 mb-6 bg-gray-100 rounded-full">
                <TabsTrigger value="queue" className="flex-1 rounded-full px-6 py-2 text-sm font-medium font-semibold text-black data-[state=active]:bg-white data-[state=active]:text-black data-[state=active]:shadow-sm">Queue</TabsTrigger>
                <TabsTrigger value="posted" className="flex-1 rounded-full px-6 py-2 text-sm font-medium font-semibold text-black data-[state=active]:bg-white data-[state=active]:text-black data-[state=active]:shadow-sm">Posted</TabsTrigger>
                <TabsTrigger value="analytics" className="flex-1 rounded-full px-6 py-2 text-sm font-medium font-semibold text-black data-[state=active]:bg-white data-[state=active]:text-black data-[state=active]:shadow-sm">Analytics</TabsTrigger>
              </TabsList>

              {/* Queue Tab */}
              <TabsContent value="queue" className="space-y-4">
                {data.queue.map((item) => (
                  <Card key={item.id}>
                    <CardContent className="p-4">
                      <div className="flex gap-4">
                        <img
                          src={item.thumbnail}
                          alt={item.title}
                          className="w-32 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold mb-1 truncate">{item.title}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span className="flex items-center gap-3">
                              <Clock className="size-4" />
                              {formatDate(item.scheduledFor)}
                            </span>
                            <div className="flex flex-col items-center mt-1 sm:flex-row sm:gap-2 sm:mt-0">
                            <span>{item.duration}</span>
                            <Badge variant={item.status === 'generating' ? 'default' : 'outline'}>
                              {item.status}
                            </Badge>
                            </div>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => navigate(`/content-editor?id=${item.id}&type=${item.type || 'video'}&platform=${item.platform || 'YouTube'}&status=${item.status}`)}
                        >
                          Edit
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              {/* Posted Tab */}
              <TabsContent value="posted" className="space-y-4">
                {data.posted.map((item) => (
                  <Card key={item.id}>
                    <CardContent className="p-4">
                      <div className="flex gap-4">
                        <img
                          src={item.thumbnail}
                          alt={item.title}
                          className="w-32 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold mb-2 truncate">{item.title}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Eye className="size-4" />
                              {formatNumber(item.views)}
                            </span>
                            <span className="flex items-center gap-1">
                              <ThumbsUp className="size-4" />
                              {formatNumber(item.likes)}
                            </span>
                            <span className="flex items-center gap-1">
                              <MessageCircle className="size-4" />
                              {item.comments}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Posted {formatDate(item.postedAt)}
                          </p>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => navigate(`/content-editor?id=${item.id}&type=${item.type || 'video'}&platform=${item.platform || 'YouTube'}&status=posted`)}
                        >
                          Edit
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              {/* Analytics Tab */}
              <TabsContent value="analytics" className="space-y-4">
                {/* Overview Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <Eye className="size-4" />
                        <span className="text-sm">Total Views</span>
                      </div>
                      <p className="text-2xl font-bold">{formatNumber(data.analytics.overview.totalViews)}</p>
                      <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                        <TrendingUp className="size-3" />
                        +{data.analytics.overview.growthRate}% this week
                      </p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <ThumbsUp className="size-4" />
                        <span className="text-sm">Total Likes</span>
                      </div>
                      <p className="text-2xl font-bold">{formatNumber(data.analytics.overview.totalLikes)}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {data.analytics.overview.avgEngagementRate}% engagement rate
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Top Performing Content */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Top Performing Content</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data.analytics.topPerformingContent.map((content, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{content.title}</p>
                          <p className="text-xs text-gray-500">{formatNumber(content.views)} views</p>
                        </div>
                        <Badge variant="outline">{content.engagementRate}% ER</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Views Over Time Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Views Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {data.analytics.viewsOverTime.map((day, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <span className="text-xs text-gray-500 w-16">{day.date.slice(5)}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-end px-2"
                              style={{ width: `${(day.views / 20000) * 100}%` }}
                            >
                              <span className="text-xs text-white font-medium">{formatNumber(day.views)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Audience Demographics */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Audience Demographics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">By Age</p>
                      <div className="space-y-2">
                        {data.analytics.audienceDemographics.byAge.map((age, idx) => (
                          <div key={idx} className="flex items-center gap-3">
                            <span className="text-xs text-gray-600 w-16">{age.range}</span>
                            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                              <div
                                className="h-full bg-purple-500 rounded-full"
                                style={{ width: `${age.percentage}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium w-10 text-right">{age.percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">By Region</p>
                      <div className="space-y-2">
                        {data.analytics.audienceDemographics.byRegion.map((region, idx) => (
                          <div key={idx} className="flex items-center gap-3">
                            <span className="text-xs text-gray-600 w-24 truncate">{region.region}</span>
                            <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                              <div
                                className="h-full bg-blue-500 rounded-full"
                                style={{ width: `${region.percentage}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium w-10 text-right">{region.percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Right Sidebar - Live Logs */}
          <div>
            <Card className="h-[calc(100vh-180px)] flex flex-col">
              <CardHeader className="flex-shrink-0">
                <CardTitle className="text-lg">Live Logs</CardTitle>
                <CardDescription>Real-time pipeline activity</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-hidden p-0">
                <ScrollArea className="h-full px-6 pb-6">
                  <div className="space-y-3">
                    {data.liveLogs.map((log) => (
                      <div key={log.id} className="flex gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                        <div className="flex-shrink-0 mt-0.5">
                          {getLogIcon(log.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm">{log.message}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatDate(log.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}