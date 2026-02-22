import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Play,
  Pause,
  Square,
  Save,
  RefreshCw,
  AlertTriangle,
  Clock,
  Sparkles,
  Edit3,
  Image as ImageIcon,
  Video,
  FileText,
  Music,
  Target,
  Calendar,
  Zap,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  Bot,
  Download,
  Trash2,
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { pipelineAPI, pipelineExecutionAPI } from '../services/api';

export function ContentEditor({ onNavigate, queueItem }) {
  const [status, setStatus] = useState(queueItem?.status || 'generating');
  const [isEditing, setIsEditing] = useState(false);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Fallback mock data (used when no run ID is provided)
  const [contentData, setContentData] = useState({
    title: 'The Future of AI in Content Creation',
    script: `Introduction (0:00-0:15):
Hey everyone! Today we're diving into something revolutionary - how AI is transforming content creation.

Main Content (0:15-2:30):
Artificial Intelligence has come a long way. From simple text generation to creating full videos, AI is now a creator's best friend. Let me show you three game-changing ways AI is being used today.

First, AI can generate scripts like this one in seconds. No more writer's block!

Second, it can create stunning visuals and thumbnails that grab attention.

Third, it automates the entire publishing workflow across platforms.

Conclusion (2:30-3:00):
The future is here, and it's automated. Thanks for watching!`,
    
    thumbnail: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=450&fit=crop',
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', // Mock video URL
    
    metadata: {
      targetAudience: 'Content creators, Digital marketers, Tech enthusiasts aged 25-45',
      keywords: ['AI', 'Content Creation', 'Automation', 'Technology', 'Productivity'],
      tone: 'Informative and enthusiastic',
      duration: '3:00',
      estimatedViews: '5K-10K',
    },
    
    generation: {
      startTime: '2026-01-18T10:30:00',
      currentStep: 'Rendering video',
      progress: 65,
      steps: [
        { name: 'Script Generation', status: 'completed', time: '10:30:15' },
        { name: 'Thumbnail Creation', status: 'completed', time: '10:31:45' },
        { name: 'Voice Synthesis', status: 'completed', time: '10:33:20' },
        { name: 'Video Rendering', status: 'in_progress', time: '10:35:00' },
        { name: 'Platform Upload', status: 'pending', time: '-' },
      ],
    },
    
    scheduling: {
      postTime: '2026-01-19T14:00:00',
      timezone: 'IST (UTC+5:30)',
      delay: 0,
    },
    
    errors: [
      {
        type: 'warning',
        message: 'Thumbnail contrast could be improved for better visibility',
        suggestion: 'Consider adding a darker overlay to the text area',
        requiresIntervention: false,
      },
    ],
    
    interventions: [
      {
        type: 'ai',
        message: 'AI detected potential copyright issue with background music',
        suggestion: 'Switched to royalty-free alternative from library',
        status: 'resolved',
      },
      {
        type: 'user',
        message: 'Script exceeds recommended length for optimal engagement',
        suggestion: 'Consider reducing to 2:30 for better retention',
        status: 'pending',
        critical: false,
      },
    ],
  });

  // Check if video is ready based on generation progress
  const isVideoReady = status === 'requires_review' || status === 'pending' || (status === 'generating' && contentData?.generation?.progress >= 80);

  const mapRunStateToStatus = (runState) => {
    if (!runState) return 'generating';
    const normalized = runState.toLowerCase();
    if (['queued', 'running'].includes(normalized)) return 'generating';
    if (normalized === 'completed') return 'completed';
    if (['hard_fail', 'halted', 'cancelled'].includes(normalized)) return 'error';
    return 'generating';
  };

  const buildContentData = (run, outputs, logs, pipeline) => {
    const scriptText = outputs?.script?.script || outputs?.composer?.caption || '';
    const firstImage = outputs?.image?.images?.[0] || outputs?.composer?.final_images?.[0];
    const thumbnail = firstImage?.s3_url || firstImage?.url || contentData.thumbnail;
    const videoUrl = outputs?.video?.video_url || outputs?.composer?.final_video_url || contentData.videoUrl;

    const steps = run?.steps || [];
    const stepItems = steps.map((step) => ({
      name: step.step_name,
      status: step.state?.toLowerCase(),
      time: step.completed_at || step.started_at || '-'
    }));

    const keywords = outputs?.composer?.metadata?.tags || outputs?.script?.metadata?.tags || [];
    const tone = outputs?.script?.metadata?.tone || pipeline?.genre || contentData.metadata.tone;
    const duration = outputs?.video?.duration_seconds || outputs?.script?.estimated_duration || contentData.metadata.duration;

    return {
      title: outputs?.composer?.metadata?.title || pipeline?.topic_value || contentData.title,
      script: scriptText || contentData.script,
      thumbnail,
      videoUrl,
      metadata: {
        ...contentData.metadata,
        tone,
        keywords,
        duration: duration ? String(duration) : contentData.metadata.duration,
      },
      generation: {
        startTime: run?.created_at || contentData.generation.startTime,
        currentStep: run?.current_step || contentData.generation.currentStep,
        progress: run?.progress_percent ?? contentData.generation.progress,
        steps: stepItems.length ? stepItems : contentData.generation.steps,
      },
      scheduling: {
        postTime: pipeline?.posting_time || contentData.scheduling.postTime,
        timezone: pipeline?.timezone || contentData.scheduling.timezone,
        delay: contentData.scheduling.delay,
      },
      errors: logs?.events?.filter((e) => e.level === 'ERROR')?.map((e) => ({
        type: 'error',
        message: e.message || e.error || 'Error',
        suggestion: '',
        requiresIntervention: false,
      })) || contentData.errors,
      interventions: contentData.interventions,
    };
  };

  useEffect(() => {
    const runId = queueItem?.id;
    if (!runId) {
      setIsLoading(false);
      return;
    }

    let intervalId;

    const loadRunData = async () => {
      try {
        setIsLoading(true);
        const run = await pipelineExecutionAPI.getRun(runId);
        let outputs = {};
        try {
          const outputsResponse = await pipelineExecutionAPI.getRunOutputs(runId);
          outputs = outputsResponse.outputs || {};
        } catch {
          outputs = run?.outputs || {};
        }

        const logs = await pipelineExecutionAPI.getRunLogs(runId, { limit: 100 });
        const pipeline = run?.pipeline_id ? await pipelineAPI.getById(run.pipeline_id) : null;

        const nextStatus = mapRunStateToStatus(run?.state);
        setStatus(nextStatus);
        setContentData(buildContentData(run, outputs, logs, pipeline));

        if (['completed', 'error'].includes(nextStatus) && intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      } catch (error) {
        console.error('Failed to load run data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRunData();
    intervalId = setInterval(loadRunData, 10000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [queueItem?.id]);
  const handlePause = () => {
    setStatus('paused');
  };

  const handleResume = () => {
    setStatus('generating');
  };

  const handleStop = () => {
    if (window.confirm('Are you sure you want to stop this content generation? This cannot be undone.')) {
      setStatus('error');
      onNavigate('pipeline/1');
    }
  };

  const handleSave = () => {
    setIsEditing(false);
    alert('Changes saved successfully!');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-gray-600 bg-gray-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getContentIcon = () => {
    const type = queueItem?.type || 'video';
    switch (type) {
      case 'video': return <Video className="size-5" />;
      case 'audio': return <Music className="size-5" />;
      case 'image': return <ImageIcon className="size-5" />;
      case 'text': return <FileText className="size-5" />;
      default: return <Video className="size-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigate('pipeline/1')}
              >
                <ArrowLeft className="size-4 mr-2" />
                Back to Pipeline
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center gap-2">
                {getContentIcon()}
                <span className="font-semibold">Content Editor</span>
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex items-center gap-2">
              {status === 'generating' && (
                <Button variant="outline" size="sm" onClick={handlePause}>
                  <Pause className="size-4 mr-2" />
                  Pause
                </Button>
              )}
              {status === 'paused' && (
                <Button variant="outline" size="sm" onClick={handleResume}>
                  <Play className="size-4 mr-2" />
                  Resume
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={handleStop} className="text-red-600 hover:text-red-700">
                <Square className="size-4 mr-2" />
                Stop
              </Button>
              <Button size="sm" onClick={handleSave} className="bg-gradient-to-r from-purple-600 to-blue-600">
                <Save className="size-4 mr-2" />
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6 max-w-7xl">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Content Preview & Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status Card */}
            <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
                      <Sparkles className="size-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Generation in Progress</h3>
                      <p className="text-sm text-gray-600">{contentData.generation.currentStep}</p>
                    </div>
                  </div>
                  <Badge className={getStatusColor(status === 'generating' ? 'in_progress' : status)}>
                    {status === 'generating' ? 'In Progress' : status}
                  </Badge>
                </div>
                <Progress value={contentData.generation.progress} className="h-2" />
                <p className="text-sm text-gray-600 mt-2">{contentData.generation.progress}% Complete</p>
              </CardContent>
            </Card>

            {/* Thumbnail & Title */}
            {(queueItem?.type === 'video' || !queueItem) && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Video Thumbnail</CardTitle>
                    <Button variant="outline" size="sm">
                      <Edit3 className="size-4 mr-2" />
                      Regenerate
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="relative rounded-lg overflow-hidden mb-4">
                    <img 
                      src={contentData.thumbnail} 
                      alt="Video thumbnail"
                      className="w-full aspect-video object-cover"
                    />
                    <div className="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-sm">
                      {contentData.metadata.duration}
                    </div>
                  </div>

                  {/* Video Player */}
                  <div className="mb-4">
                    <Label className="mb-2 block">Video Preview</Label>
                    {isVideoReady ? (
                      <div className="relative rounded-lg overflow-hidden bg-black group">
                        <video 
                          className="w-full aspect-video object-contain"
                          controls={isVideoPlaying}
                          onClick={() => setIsVideoPlaying(true)}
                        >
                          <source src={contentData.videoUrl} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                        {!isVideoPlaying && (
                          <div 
                            className="absolute inset-0 flex items-center justify-center bg-black/40 cursor-pointer group-hover:bg-black/50 transition-colors"
                            onClick={() => setIsVideoPlaying(true)}
                          >
                            <div className="bg-white rounded-full p-4 group-hover:scale-110 transition-transform">
                              <Play className="size-8 text-purple-600 fill-purple-600" />
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="relative rounded-lg overflow-hidden bg-gradient-to-br from-purple-100 to-blue-100 border-2 border-purple-200">
                        <div className="w-full aspect-video flex flex-col items-center justify-center p-8">
                          <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-4 rounded-full mb-4 animate-pulse">
                            <Video className="size-8 text-white" />
                          </div>
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">Video is Being Created</h3>
                          <p className="text-sm text-gray-600 text-center max-w-md">
                            AI is currently rendering your video. This usually takes 2-5 minutes.
                          </p>
                          <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
                            <RefreshCw className="size-4 animate-spin" />
                            <span>{contentData.generation.progress}% Complete</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Title</Label>
                    <Input 
                      value={contentData.title}
                      onChange={(e) => setContentData({...contentData, title: e.target.value})}
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Script Editor */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>AI-Generated Script</CardTitle>
                    <CardDescription>Edit and refine the content before publishing</CardDescription>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setIsEditing(!isEditing)}
                  >
                    <Edit3 className="size-4 mr-2" />
                    {isEditing ? 'Preview' : 'Edit'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <Textarea 
                  value={contentData.script}
                  onChange={(e) => setContentData({...contentData, script: e.target.value})}
                  className="min-h-[400px] font-mono text-sm"
                  disabled={!isEditing}
                />
                <div className="flex items-center justify-between mt-4 text-sm text-gray-600">
                  <span>{contentData.script.split(' ').length} words</span>
                  <span>{contentData.script.split('\n').length} lines</span>
                </div>
              </CardContent>
            </Card>

            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Content Intelligence</CardTitle>
                <CardDescription>AI-analyzed metadata and targeting</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="flex items-center gap-2 mb-2">
                    <Target className="size-4 text-purple-600" />
                    Target Audience
                  </Label>
                  <p className="text-sm text-gray-700 p-3 bg-gray-50 rounded-lg">
                    {contentData.metadata.targetAudience}
                  </p>
                </div>

                <div>
                  <Label className="flex items-center gap-2 mb-2">
                    <Zap className="size-4 text-blue-600" />
                    Keywords & Tags
                  </Label>
                  <div className="flex flex-wrap gap-2">
                    {contentData.metadata.keywords.map((keyword, idx) => (
                      <Badge key={idx} variant="outline">{keyword}</Badge>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm text-gray-600">Tone</Label>
                    <p className="font-medium">{contentData.metadata.tone}</p>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">Est. Views</Label>
                    <p className="font-medium">{contentData.metadata.estimatedViews}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Errors & Warnings */}
            {contentData.errors.length > 0 && (
              <Card className="border-yellow-300 bg-yellow-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-yellow-800">
                    <AlertTriangle className="size-5" />
                    Warnings & Suggestions
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {contentData.errors.map((error, idx) => (
                    <div key={idx} className="p-4 bg-white rounded-lg border border-yellow-200">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="size-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-medium text-yellow-900">{error.message}</p>
                          <p className="text-sm text-yellow-700 mt-1">{error.suggestion}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Scheduling */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="size-5 text-purple-600" />
                  Scheduling
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-sm text-gray-600">Post Time</Label>
                  <p className="font-medium">
                    {new Date(contentData.scheduling.postTime).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{contentData.scheduling.timezone}</p>
                </div>

                <Separator />

                <div>
                  <Label className="text-sm text-gray-600">Delay Status</Label>
                  {contentData.scheduling.delay === 0 ? (
                    <div className="flex items-center gap-2 text-green-600 mt-1">
                      <CheckCircle className="size-4" />
                      <span className="text-sm font-medium">On Schedule</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-red-600 mt-1">
                      <Clock className="size-4" />
                      <span className="text-sm font-medium">Delayed by {contentData.scheduling.delay} mins</span>
                    </div>
                  )}
                </div>

                <Button variant="outline" className="w-full">
                  <Clock className="size-4 mr-2" />
                  Reschedule
                </Button>
              </CardContent>
            </Card>

            {/* Generation Steps */}
            <Card>
              <CardHeader>
                <CardTitle>Generation Pipeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {contentData.generation.steps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <div className="mt-1">
                        {step.status === 'completed' && (
                          <CheckCircle className="size-5 text-green-600" />
                        )}
                        {step.status === 'in_progress' && (
                          <RefreshCw className="size-5 text-blue-600 animate-spin" />
                        )}
                        {step.status === 'pending' && (
                          <div className="size-5 rounded-full border-2 border-gray-300" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{step.name}</p>
                        <p className="text-xs text-gray-500">
                          {step.status === 'pending' ? 'Waiting...' : step.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Interventions Required */}
            {contentData.interventions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Interventions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {contentData.interventions.map((intervention, idx) => (
                    <div 
                      key={idx} 
                      className={`p-4 rounded-lg border-2 ${
                        intervention.type === 'ai' 
                          ? 'bg-blue-50 border-blue-200' 
                          : 'bg-orange-50 border-orange-200'
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        {intervention.type === 'ai' ? (
                          <Bot className="size-5 text-blue-600 mt-0.5" />
                        ) : (
                          <User className="size-5 text-orange-600 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold uppercase">
                              {intervention.type === 'ai' ? 'AI Auto-Fixed' : 'User Review Needed'}
                            </span>
                            {intervention.status === 'resolved' && (
                              <CheckCircle className="size-4 text-green-600" />
                            )}
                          </div>
                        </div>
                      </div>
                      <p className="text-sm font-medium mb-1">{intervention.message}</p>
                      <p className="text-xs text-gray-700">{intervention.suggestion}</p>
                      {intervention.type === 'user' && intervention.status === 'pending' && (
                        <div className="mt-3 flex gap-2">
                          <Button size="sm" className="flex-1">Accept</Button>
                          <Button size="sm" variant="outline" className="flex-1">Ignore</Button>
                        </div>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Download className="size-4 mr-2" />
                  Download Draft
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <RefreshCw className="size-4 mr-2" />
                  Regenerate Content
                </Button>
                <Button variant="outline" className="w-full justify-start text-red-600 hover:text-red-700">
                  <Trash2 className="size-4 mr-2" />
                  Delete Queue Item
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
