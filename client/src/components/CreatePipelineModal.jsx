import { useState } from 'react';
import { X, Sparkles, Link as LinkIcon, Info, Upload, FileText, Image as ImageIcon, Video, Music, FileX } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Separator } from './ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';
import { pipelineAPI, assetAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const platforms = [
  'YouTube',
  'Instagram',
  'LinkedIn',
  'Reddit',
  'Medium',
  'Twitter/X',
  'Facebook',
  'TikTok',
  'Pinterest',
];

const contentTypes = [
  'Text',
  'Video',
  'Audio',
  'Image',
  'All/Any',
];

const agentModels = [
  'GPT-4',
  'GPT-3.5 Turbo',
  'Claude 3 Opus',
  'Claude 3 Sonnet',
  'Gemini Pro',
  'Llama 3',
];

const videoProviders = [
  { value: 'replicate', label: 'Replicate' },
  { value: 'runway', label: 'Runway' },
  { value: 'comfyui', label: 'ComfyUI (Local)' },
];

const videoAspectRatios = [
  '16:9',
  '9:16',
  '1:1',
  '4:3',
];

const videoModels = [
  'stability-ai/stable-video-diffusion',
  'zeroscope-v2-576w',
  'video-animator',
];

const timezones = [
  'IST (Indian Standard Time)',
  'PST (Pacific Standard Time)',
  'EST (Eastern Standard Time)',
  'GMT (Greenwich Mean Time)',
  'CST (Central Standard Time)',
  'JST (Japan Standard Time)',
  'AEST (Australian Eastern Standard Time)',
];

const frequencies = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const genres = [
  'All',
  'Technology',
  'Business',
  'Entertainment',
  'Education',
  'Lifestyle',
  'Health & Fitness',
  'Gaming',
  'News',
  'Comedy',
  'Science',
  'Arts & Culture',
];

const topicTypes = [
  'Trending',
  'Topic of the Day',
  'Topic of the Region',
  'Specific Topic',
];

const regions = [
  'Global',
  'North America',
  'South America',
  'Europe',
  'Asia',
  'Africa',
  'Middle East',
  'Oceania',
  'United States',
  'India',
  'United Kingdom',
  'Canada',
  'Australia',
];

export function CreatePipelineModal({ open, onOpenChange, onPipelineCreated }) {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    platform: '',
    contentType: '',
    agentModel: '',
    manualIntervention: false,
    additionalPrompts: '',
    referenceFiles: [],
    time: '',
    timezone: '',
    frequency: 'weekly',
    frequencyCount: '1',
    temperature: [0.7],
    genre: 'All',
    topicType: '',
    specificTopic: '',
    regions: [],
    videoProvider: 'replicate',
    videoModel: 'stability-ai/stable-video-diffusion',
    videoDuration: '4',
    videoAspectRatio: '16:9',
    videoFps: '24',
  });

  const [connectedPlatforms, setConnectedPlatforms] = useState([]);

  // Upload reference files to S3 using presigned URLs
  const uploadReferenceFiles = async (pipelineId, files) => {
    if (files.length === 0) return;

    try {
      // Step 1: Request upload URLs for all files
      console.log(`📤 Requesting upload URLs for ${files.length} files...`);
      const uploadResponse = await assetAPI.requestUploadUrls(pipelineId, files);

      // Step 2: Upload each file directly to S3
      const uploadPromises = uploadResponse.uploads.map(async (uploadData, index) => {
        const file = files[index];
        
        try {
          console.log(`⬆️  Uploading ${file.name} to S3...`);
          
          // Upload directly to S3
          await assetAPI.uploadToS3(
            uploadData.upload_url,
            uploadData.upload_fields,
            file
          );

          // Step 3: Confirm successful upload
          await assetAPI.confirmUpload(pipelineId, uploadData.asset_id, true);
          
          console.log(`✅ ${file.name} uploaded successfully`);
          return { success: true, filename: file.name };
        } catch (error) {
          console.error(`❌ Failed to upload ${file.name}:`, error);
          
          // Confirm failed upload
          await assetAPI.confirmUpload(
            pipelineId, 
            uploadData.asset_id, 
            false, 
            error.message
          );
          
          return { success: false, filename: file.name, error: error.message };
        }
      });

      const results = await Promise.all(uploadPromises);
      const successCount = results.filter(r => r.success).length;
      const failedCount = results.filter(r => !r.success).length;

      console.log(`📊 Upload complete: ${successCount} succeeded, ${failedCount} failed`);

      if (failedCount > 0) {
        throw new Error(`${failedCount} file(s) failed to upload`);
      }
    } catch (error) {
      console.error('Error in uploadReferenceFiles:', error);
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Validate required fields
      if (!formData.platform || !formData.contentType || !formData.agentModel || 
          !formData.time || !formData.timezone || !formData.topicType) {
        toast({
          title: "Validation Error",
          description: "Please fill in all required fields marked with *",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      if (formData.topicType === 'Specific Topic' && !formData.specificTopic) {
        toast({
          title: "Validation Error",
          description: "Please enter a specific topic",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      if (formData.regions.length === 0) {
        toast({
          title: "Validation Error",
          description: "Please select at least one target region",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      // Map frontend form data to backend schema
      const pipelineData = {
        platform: formData.platform.toLowerCase().replace('/', '').replace('twitter/x', 'twitter'),
        content_type: formData.contentType === 'All/Any' ? 'any' : formData.contentType.toLowerCase(),
        agent_model: formData.agentModel
          .toLowerCase()
          .replace('gpt-4', 'gpt-4')
          .replace('gpt-3.5 turbo', 'gpt-3.5-turbo')
          .replace('claude 3 opus', 'claude-3-opus')
          .replace('claude 3 sonnet', 'claude-3-sonnet')
          .replace('gemini pro', 'gemini-pro')
          .replace('llama 3', 'llama3')
          .replace(/ /g, '-'),
        manual_review: formData.manualIntervention,
        additional_prompt: formData.additionalPrompts || null,
        posting_time: formData.time,
        timezone: formData.timezone.split(' ')[0],
        frequency: formData.frequency,
        times_per_week: formData.frequency === 'weekly' ? parseInt(formData.frequencyCount) : null,
        temperature: formData.temperature[0],
        connected_accounts: connectedPlatforms.reduce((acc, platform) => {
          acc[platform] = { connected: true, timestamp: new Date().toISOString() };
          return acc;
        }, {}),
        genre: formData.genre === 'All' ? 'all' : 
               formData.genre === 'Technology' ? 'tech' :
               formData.genre === 'Business' ? 'business' :
               formData.genre === 'Entertainment' ? 'entertainment' :
               formData.genre === 'Education' ? 'education' :
               formData.genre === 'Lifestyle' ? 'lifestyle' :
               formData.genre === 'Health & Fitness' ? 'health_fitness' :
               formData.genre === 'Gaming' ? 'gaming' :
               formData.genre === 'News' ? 'news' :
               formData.genre === 'Comedy' ? 'comedy' :
               formData.genre === 'Science' ? 'science' :
               formData.genre.toLowerCase().replace(/ /g, '_').replace(/&/g, ''),
        topic_type: formData.topicType === 'Trending' ? 'trending' :
                    formData.topicType === 'Topic of the Day' ? 'topic_of_the_day' :
                    formData.topicType === 'Topic of the Region' ? 'topic_of_the_region' :
                    formData.topicType === 'Specific Topic' ? 'specific' :
                    formData.topicType.toLowerCase().replace(/ /g, '_'),
        topic_value: formData.topicType === 'Specific Topic' ? formData.specificTopic : null,
        target_regions: formData.regions,
        video_provider: formData.videoProvider,
        video_model: formData.videoModel,
        video_duration_seconds: parseInt(formData.videoDuration) || null,
        video_aspect_ratio: formData.videoAspectRatio,
        video_fps: parseInt(formData.videoFps) || null,
      };

      const response = await pipelineAPI.create(pipelineData);

      // Upload reference files if any
      if (formData.referenceFiles.length > 0) {
        try {
          await uploadReferenceFiles(response.id, formData.referenceFiles);
          toast({
            title: "Pipeline Created!",
            description: `Pipeline created successfully with ${formData.referenceFiles.length} reference file(s).`,
          });
        } catch (uploadError) {
          console.error('Error uploading files:', uploadError);
          toast({
            title: "Pipeline Created (File Upload Failed)",
            description: "Pipeline created but some files failed to upload. You can add them later.",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "Pipeline Created!",
          description: "Your content automation pipeline has been created successfully.",
        });
      }

      // Reset form
      setFormData({
        platform: '',
        contentType: '',
        agentModel: '',
        manualIntervention: false,
        additionalPrompts: '',
        referenceFiles: [],
        time: '',
        timezone: '',
        frequency: 'weekly',
        frequencyCount: '1',
        temperature: [0.7],
        genre: 'All',
        topicType: '',
        specificTopic: '',
        regions: [],
        videoProvider: 'replicate',
        videoModel: 'stability-ai/stable-video-diffusion',
        videoDuration: '4',
        videoAspectRatio: '16:9',
        videoFps: '24',
      });
      setConnectedPlatforms([]);

      if (onPipelineCreated) {
        onPipelineCreated(response);
      }

      onOpenChange(false);
    } catch (error) {
      console.error('Error creating pipeline:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to create pipeline. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleRegion = (region) => {
    setFormData({
      ...formData,
      regions: formData.regions.includes(region)
        ? formData.regions.filter(r => r !== region)
        : [...formData.regions, region],
    });
  };

  const connectPlatform = (platform) => {
    if (!connectedPlatforms.includes(platform)) {
      setConnectedPlatforms([...connectedPlatforms, platform]);
      // In a real app, this would trigger OAuth flow
      console.log(`Connecting to ${platform}...`);
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => {
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: `${file.name} exceeds 50MB limit`,
          variant: "destructive",
        });
        return false;
      }
      return true;
    });
    
    setFormData({
      ...formData,
      referenceFiles: [...formData.referenceFiles, ...validFiles]
    });
  };

  const removeFile = (index) => {
    setFormData({
      ...formData,
      referenceFiles: formData.referenceFiles.filter((_, i) => i !== index)
    });
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) {
      return <ImageIcon className="size-4" />;
    }
    if (['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext)) {
      return <Video className="size-4" />;
    }
    if (['mp3', 'wav', 'ogg', 'm4a', 'flac'].includes(ext)) {
      return <Music className="size-4" />;
    }
    return <FileText className="size-4" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl text-black">
            <Sparkles className="size-6 text-purple-600" />
            Create New Pipeline
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            Configure your automated content creation workflow
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          {/* Platform Selection */}
          <div className="space-y-2">
            <Label htmlFor="platform" className="flex items-center gap-2 text-black">
              Platform
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="size-4 text-gray-400" />
                  </TooltipTrigger>
                  <TooltipContent className="text-black border">
                    <p>Choose where your content will be published</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <Select value={formData.platform} onValueChange={(value) => setFormData({...formData, platform: value})}>
              <SelectTrigger className="text-black border-gray-300">
                <SelectValue placeholder="Select platform" />
              </SelectTrigger>
              <SelectContent className="text-black">
                {platforms.map((platform) => (
                  <SelectItem key={platform} value={platform}>
                    {platform}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Content Type */}
          <div className="space-y-2">
            <Label htmlFor="contentType" className="text-black">Content Type</Label>
            <Select value={formData.contentType} onValueChange={(value) => setFormData({...formData, contentType: value})}>
              <SelectTrigger className="text-black border-gray-300">
                <SelectValue placeholder="Select content type" />
              </SelectTrigger>
              <SelectContent className="bg-white text-black">
                {contentTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Agent Model */}
          <div className="space-y-2">
            <Label htmlFor="agentModel" className="flex items-center gap-2 text-black">
              Agent Model
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="size-4 text-gray-400" />
                  </TooltipTrigger>
                  <TooltipContent className="bg-white text-gray-500 border border-gray-300">
                    <p>AI model used to generate your content script</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <Select value={formData.agentModel} onValueChange={(value) => setFormData({...formData, agentModel: value})}>
              <SelectTrigger className="text-black border-gray-300">
                <SelectValue placeholder="Select AI model" />
              </SelectTrigger>
              <SelectContent className="text-black">
                {agentModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Video Provider Settings (Video only) */}
          {formData.contentType === 'Video' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="videoProvider" className="text-black">Video Provider</Label>
                <Select
                  value={formData.videoProvider}
                  onValueChange={(value) => setFormData({ ...formData, videoProvider: value })}
                >
                  <SelectTrigger className="text-black border-gray-300">
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent className="text-black">
                    {videoProviders.map((provider) => (
                      <SelectItem key={provider.value} value={provider.value}>
                        {provider.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="videoModel" className="text-black">Video Model</Label>
                <Select
                  value={formData.videoModel}
                  onValueChange={(value) => setFormData({ ...formData, videoModel: value })}
                >
                  <SelectTrigger className="text-black border-gray-300">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent className="text-black">
                    {videoModels.map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="videoDuration" className="text-black">Duration (sec)</Label>
                  <Input
                    id="videoDuration"
                    type="number"
                    min="1"
                    value={formData.videoDuration}
                    onChange={(e) => setFormData({ ...formData, videoDuration: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="videoAspectRatio" className="text-black">Aspect Ratio</Label>
                  <Select
                    value={formData.videoAspectRatio}
                    onValueChange={(value) => setFormData({ ...formData, videoAspectRatio: value })}
                  >
                    <SelectTrigger className="text-black border-gray-300">
                      <SelectValue placeholder="Aspect ratio" />
                    </SelectTrigger>
                    <SelectContent className="text-black">
                      {videoAspectRatios.map((ratio) => (
                        <SelectItem key={ratio} value={ratio}>
                          {ratio}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="videoFps" className="text-black">FPS</Label>
                  <Input
                    id="videoFps"
                    type="number"
                    min="1"
                    value={formData.videoFps}
                    onChange={(e) => setFormData({ ...formData, videoFps: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Manual Intervention */}
          <div className="space-y-2">
            <div className="flex items-center justify-between p-4 border border-gray-300 rounded-lg bg-gray-200">
              <div className="flex-1">
                <Label htmlFor="manualIntervention" className="flex items-center gap-2 text-black cursor-pointer">
                  Manual Intervention Before Posting
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <Info className="size-4 text-gray-400" />
                      </TooltipTrigger>
                      <TooltipContent className="bg-white text-black border max-w-xs">
                        <p>When enabled, content will be queued for your review and approval before posting</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </Label>
                <p className="text-xs text-gray-600 mt-1">
                  Review and approve content before it's published
                </p>
              </div>
              <Button
                type="button"
                variant={formData.manualIntervention ? "default" : "outline"}
                size="sm"
                onClick={() => setFormData({...formData, manualIntervention: !formData.manualIntervention})}
                className={formData.manualIntervention ? "bg-gradient-to-r from-purple-600 to-blue-600" : "text-black"}
              >
                {formData.manualIntervention ? "Enabled" : "Disabled"}
              </Button>
            </div>
          </div>

          {/* Additional Prompts */}
          <div className="space-y-2">
            <Label htmlFor="prompts" className="text-black">Additional User Prompts</Label>
            <Textarea
            className="border-gray-300"
              id="prompts"
              placeholder="Add specific instructions for content generation (e.g., tone, style, specific topics to cover...)"
              value={formData.additionalPrompts}
              onChange={(e) => setFormData({...formData, additionalPrompts: e.target.value})}
              rows={4}
            />
          </div>

          {/* Reference Files Upload */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2 text-black">
              Reference Materials
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="size-4 text-gray-400" />
                  </TooltipTrigger>
                  <TooltipContent className="bg-white text-black border max-w-xs">
                    <p>Upload images, videos, audio, or documents as reference for content generation. Max 50MB per file.</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-200 hover:border-purple-400 transition-colors">
              <input
                type="file"
                id="fileUpload"
                multiple
                accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt,.md"
                onChange={handleFileChange}
                className="hidden"
              />
              <label
                htmlFor="fileUpload"
                className="flex flex-col items-center justify-center cursor-pointer"
              >
                <Upload className="size-8 text-gray-400 mb-2" />
                <p className="text-sm text-black font-medium">Click to upload reference files</p>
                <p className="text-xs text-gray-500 mt-1">Images, videos, audio, documents (Max 50MB each)</p>
              </label>
            </div>
            
            {/* Display uploaded files */}
            {formData.referenceFiles.length > 0 && (
              <div className="space-y-2 mt-3">
                <p className="text-sm font-medium text-black">
                  {formData.referenceFiles.length} file(s) uploaded
                </p>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {formData.referenceFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-200 border border-gray-200 rounded-lg"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="text-purple-600">
                          {getFileIcon(file.name)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-black truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <FileX className="size-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <Separator />

          {/* Time and Timezone */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="time" className="text-black">Posting Time</Label>
              <Input
              className={`bg-gray-200 border-gray-300 ${formData.time ? 'text-black' : 'text-gray-400'}`}
                id="time"
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({...formData, time: e.target.value})}
                style={{
                  colorScheme: 'light'
                }}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone" className="text-black">Timezone</Label>
              <Select value={formData.timezone} onValueChange={(value) => setFormData({...formData, timezone: value})}>
                <SelectTrigger className="text-black border-gray-300">
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent className="bg-white text-black">
                  {timezones.map((tz) => (
                    <SelectItem key={tz} value={tz}>
                      {tz}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Frequency */}
          <div className="space-y-2">
            <Label className="text-black">Frequency</Label>
            <div className="grid md:grid-cols-2 gap-4">
              <Select value={formData.frequency} onValueChange={(value) => setFormData({...formData, frequency: value})}>
                <SelectTrigger className="text-black border-gray-300">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white text-black">
                  {frequencies.map((freq) => (
                    <SelectItem key={freq.value} value={freq.value}>
                      {freq.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex items-center gap-2">
                <Input
                className="bg-gray-200 text-black w-20 border-gray-300"
                  type="number"
                  min="1"
                  max="30"
                  value={formData.frequencyCount}
                  onChange={(e) => setFormData({...formData, frequencyCount: e.target.value})}
                />
                <span className="text-sm text-gray-600">
                  times per {formData.frequency === 'daily' ? 'day' : formData.frequency === 'weekly' ? 'week' : 'month'}
                </span>
              </div>
            </div>
          </div>

          {/* Temperature */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="flex items-center gap-2 text-black">
                Temperature
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Info className="size-4 text-gray-400" />
                    </TooltipTrigger>
                    <TooltipContent className="bg-white text-black border">
                      <p>Lower = More Factual, Higher = More Creative/Storytelling</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </Label>
              <span className="text-sm font-medium text-black">{formData.temperature[0].toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-gray-600">Factual</span>
              <Slider
                value={formData.temperature}
                onValueChange={(value) => setFormData({...formData, temperature: value})}
                min={0}
                max={1}
                step={0.1}
                className="flex-1 text-black bg-white"
              />
              <span className="text-xs text-gray-600">Creative</span>
            </div>
          </div>

          <Separator />

          {/* Social Media Connection */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-black">
              Social Media Connection
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="size-4 text-gray-400" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs bg-white text-black border">
                    <p>Connect your social media accounts using OAuth authentication. This allows FlowForge to post content on your behalf securely.</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <div className="p-4 border border-gray-300 rounded-lg bg-gray-100 text-gray-500">
              <p className="text-sm text-black mb-3">
                {formData.platform ? `Connect your ${formData.platform} account to enable automated posting` : 'Select a platform first'}
              </p>
              {formData.platform && (
                <div className="flex items-center gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => connectPlatform(formData.platform)}
                    disabled={connectedPlatforms.includes(formData.platform)}
                  >
                    <LinkIcon className="size-4 mr-2" />
                    {connectedPlatforms.includes(formData.platform) ? 'Connected' : `Connect ${formData.platform}`}
                  </Button>
                  {connectedPlatforms.includes(formData.platform) && (
                    <Badge className="bg-green-100 text-green-700 border-green-200">
                      ✓ Connected
                    </Badge>
                  )}
                </div>
              )}
              <p className="text-xs text-gray-600 mt-2">
                🔒 Your credentials are encrypted and never stored on our servers
              </p>
            </div>
          </div>

          {/* Genre */}
          <div className="space-y-2">
            <Label htmlFor="genre" className="text-black">Genre</Label>
            <Select value={formData.genre} onValueChange={(value) => setFormData({...formData, genre: value})}>
              <SelectTrigger className="text-black border-gray-300">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white text-black">
                {genres.map((genre) => (
                  <SelectItem key={genre} value={genre}>
                    {genre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Topic */}
          <div className="space-y-2">
            <Label htmlFor="topicType" className="text-black">Topic</Label>
            <Select value={formData.topicType} onValueChange={(value) => setFormData({...formData, topicType: value})}>
              <SelectTrigger className="text-black border-gray-300">
                <SelectValue placeholder="Select topic type" />
              </SelectTrigger>
              <SelectContent className="bg-white text-black">
                {topicTypes.map((topic) => (
                  <SelectItem key={topic} value={topic}>
                    {topic}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {formData.topicType === 'Specific Topic' && (
              <Input
                placeholder="Enter specific topic..."
                value={formData.specificTopic}
                onChange={(e) => setFormData({...formData, specificTopic: e.target.value})}
                className="mt-2 bg-white text-black border-gray-300"
              />
            )}
          </div>

          {/* Region */}
          <div className="space-y-2">
            <Label className="text-black">Target Region(s)</Label>
            <div className="p-4 border border-gray-300 rounded-lg bg-gray-100 max-h-48 overflow-y-auto">
              <div className="flex flex-wrap gap-2 ">
                {regions.map((region) => (
                  <Badge
                    key={region}
                    variant="outline"
                    className={`cursor-pointer transition-colors ${
                      formData.regions.includes(region)
                        ? 'bg-purple-100 border-purple-500 text-purple-700'
                        : 'hover:bg-gray-100 text-black border-gray-300'
                    }`}
                    onClick={() => toggleRegion(region)}
                  >
                    {region}
                    {formData.regions.includes(region) && ' ✓'}
                  </Badge>
                ))}
              </div>
            </div>
            <p className="text-xs text-gray-600">
              {formData.regions.length === 0 ? 'Select one or more regions' : `${formData.regions.length} region(s) selected`}
            </p>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button 
              type="button" 
              variant="outline" 
              className="text-black border border-gray-300" 
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="bg-gradient-to-r from-purple-600 to-blue-600"
              disabled={isSubmitting}
            >
              <Sparkles className="size-4 mr-2" />
              {isSubmitting ? 'Creating...' : 'Create Pipeline'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}