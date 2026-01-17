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

import userData from "../data/userData.json";

export function Dashboard() {
  const navigate = useNavigate();

  const [pipelines, setPipelines] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Load pipelines from localStorage
  useEffect(() => {
    loadPipelines();
  }, []);

  const loadPipelines = () => {
    const stored = localStorage.getItem("flowforge-pipelines");
    if (stored) {
      setPipelines(JSON.parse(stored));
    }
  };

  const handlePipelineCreated = () => {
    loadPipelines();
  };

  const togglePause = (id) => {
    const updatedPipelines = pipelines.map((p) =>
      p.id === id
        ? {
            ...p,
            status: p.status === "active" ? "paused" : "active",
          }
        : p,
    );

    setPipelines(updatedPipelines);
    localStorage.setItem(
      "flowforge-pipelines",
      JSON.stringify(updatedPipelines),
    );
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
    if (pipeline.topicType === "Specific Topic" && pipeline.specificTopic) {
      return pipeline.specificTopic;
    }
    return pipeline.topicType || "No topic specified";
  };

  const formatPostingTime = (pipeline) => {
    if (!pipeline.time || !pipeline.timezone) {
      return "Not set";
    }
    const timezoneName = pipeline.timezone.split("(")[0].trim();
    return `${pipeline.time} ${timezoneName}`;
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

        {pipelines.length === 0 ? (
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
                {pipelines.map((pipeline) => (
                  <TableRow key={pipeline.id}>
                    <TableCell className="font-medium">
                      {pipeline.platform}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {getDescription(pipeline)}
                    </TableCell>
                    <TableCell>{pipeline.agentModel}</TableCell>
                    <TableCell>{pipeline.contentType}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {pipeline.regions.slice(0, 2).map((region, idx) => (
                          <Badge
                            key={idx}
                            variant="outline"
                            className="text-xs"
                          >
                            {region}
                          </Badge>
                        ))}
                        {pipeline.regions.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{pipeline.regions.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={getStatusColor(pipeline.status)}
                          variant="outline"
                        >
                          {pipeline.status}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => togglePause(pipeline.id)}
                        >
                          {pipeline.status === "active" ? (
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
                ))}
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
