import { useState, useEffect } from "react";
import {
  Plus,
  Play,
  Pause,
  Eye,
  Zap,
  User,
  CreditCard,
  Sparkles,
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Card } from "./ui/card";
import { CreatePipelineModal } from "./CreatePipelineModal";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import { pipelineAPI } from "../services/api";
import { useToast } from "../hooks/use-toast";

import userData from "../data/userData.json";

export function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [pipelines, setPipelines] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load pipelines from backend API
  useEffect(() => {
    loadPipelines();
  }, []);

  const loadPipelines = async () => {
    try {
      setIsLoading(true);
      const data = await pipelineAPI.getAll();
      setPipelines(data);
    } catch (error) {
      console.error('Error loading pipelines:', error);
      toast({
        title: "Error",
        description: "Failed to load pipelines. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePipelineCreated = (newPipeline) => {
    // Refresh the pipeline list
    loadPipelines();
  };

  const togglePause = async (id) => {
    // Note: Status field not yet in backend model
    // For now, update locally only
    const updatedPipelines = pipelines.map((p) =>
      p.id === id
        ? {
            ...p,
            status: p.status === "active" ? "paused" : "active",
          }
        : p,
    );

    setPipelines(updatedPipelines);
    // TODO: Call backend API when status field is added to pipeline model
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-700 border-green-200";
      case "paused":
        return "bg-yellow-100 text-yellow-700 border-yellow-200";
      case "error":
        return "bg-red-100 text-red-700 border-red-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  const getDescription = (pipeline) => {
    // Handle both frontend and backend data structures
    const topicType = pipeline.topic_type || pipeline.topicType;
    const topicValue = pipeline.topic_value || pipeline.specificTopic;
    
    if ((topicType === 'specific' || topicType === 'Specific Topic') && topicValue) {
      return topicValue;
    }
    
    // Convert backend enum to display format
    if (topicType === 'topic_of_the_day') return 'Topic of the Day';
    if (topicType === 'topic_of_the_region') return 'Topic of the Region';
    if (topicType === 'trending') return 'Trending';
    
    return topicType || "No topic specified";
  };

  const formatPostingTime = (pipeline) => {
    // Handle both frontend and backend data structures
    const time = pipeline.posting_time || pipeline.time;
    const timezone = pipeline.timezone;
    
    if (!time || !timezone) {
      return "Not set";
    }
    
    // Handle timezone format - if it includes description, extract code
    const timezoneName = timezone.includes("(") ? timezone.split("(")[0].trim() : timezone;
    return `${time} ${timezoneName}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}

      <Navbar
        variant="profile"
        onNavigate={(page) => navigate(`/${page}`)}
        userData={userData}
        backTarget=""
      />

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-black">
              Your Pipelines
            </h1>
            <p className="text-gray-600">
              Manage your automated content workflows
            </p>
          </div>
          <Button
            className="bg-gradient-to-r from-purple-600 to-blue-600"
            onClick={() => setIsCreateModalOpen(true)}
          >
            <Plus className="size-5 mr-2" />
            Add Pipeline
          </Button>
        </div>

        {isLoading ? (
          <Card className="p-12 text-center">
            <div className="max-w-md mx-auto">
              <Sparkles className="size-12 mx-auto mb-4 text-purple-600 animate-pulse" />
              <p className="text-gray-600">Loading your pipelines...</p>
            </div>
          </Card>
        ) : pipelines.length === 0 ? (
          <Card className="p-12 text-center bg-gray-900 border-2">
            <div className="max-w-md mx-auto">
              <div className="mb-6 flex justify-end">
                {/* <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopyCode}
                  className="text-gray-400 hover:text-white"
                >
                  <Copy className="size-4 mr-2" />
                  Copy code
                </Button> */}
              </div>

              <div className="font-mono text-left bg-gray-950 rounded-lg p-6 border border-gray-800">
                <div className="mb-4">
                  <span className="text-blue-400">No</span>
                  <span className="text-gray-300"> pipelines yet.</span>
                </div>
                <div className="text-gray-300">
                  <span className="text-gray-500">[</span>{" "}
                  <span className="text-purple-400">Create</span>{" "}
                  <span className="text-gray-300">your</span>{" "}
                  <span className="text-blue-400">first</span>{" "}
                  <span className="text-gray-300">automation</span>{" "}
                  <span className="text-gray-500">]</span>
                </div>
              </div>

              <Button
                className="mt-8 bg-gradient-to-r from-purple-600 to-blue-600"
                size="lg"
                onClick={() => setIsCreateModalOpen(true)}
              >
                <Sparkles className="size-5 mr-2" />
                Create Your First Pipeline
              </Button>
            </div>
          </Card>
        ) : (
          <Card className="border-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Platform</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Agent Model</TableHead>
                  <TableHead>Content Type</TableHead>
                  <TableHead>Region</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Posting Time</TableHead>
                  <TableHead className="text-center">View</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pipelines.map((pipeline) => {
                  // Handle both frontend and backend data structures
                  const agentModel = pipeline.agent_model || pipeline.agentModel;
                  const contentType = pipeline.content_type || pipeline.contentType;
                  const regions = pipeline.target_regions || pipeline.regions || [];
                  const status = pipeline.status || "active"; // Default to active
                  
                  return (
                  <TableRow key={pipeline.id}>
                    <TableCell className="font-medium">
                      {pipeline.platform}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {getDescription(pipeline)}
                    </TableCell>
                    <TableCell>{agentModel}</TableCell>
                    <TableCell>{contentType}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {regions.slice(0, 2).map((region, idx) => (
                          <Badge
                            key={idx}
                            variant="outline"
                            className="text-xs"
                          >
                            {region}
                          </Badge>
                        ))}
                        {regions.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{regions.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={getStatusColor(status)}
                          variant="outline"
                        >
                          {status}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => togglePause(pipeline.id)}
                        >
                          {status === "active" ? (
                            <Pause className="size-4" />
                          ) : (
                            <Play className="size-4" />
                          )}
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell>{formatPostingTime(pipeline)}</TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/pipeline/${pipeline.id}`)}
                      >
                        <Eye className="size-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Card>
        )}
      </main>

      <CreatePipelineModal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onPipelineCreated={handlePipelineCreated}
      />
    </div>
  );
}
