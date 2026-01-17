import { useState } from 'react';
import { X, Sparkles, Link as LinkIcon, Info } from 'lucide-react';
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
  const [formData, setFormData] = useState({
    platform: '',
    contentType: '',
    agentModel: '',
    manualIntervention: false,
    additionalPrompts: '',
    time: '',
    timezone: '',
    frequency: 'weekly',
    frequencyCount: '1',
    temperature: [0.7],
    genre: 'All',
    topicType: '',
    specificTopic: '',
    regions: [],
  });

  const [connectedPlatforms, setConnectedPlatforms] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Create pipeline object
    const pipeline = {
      id: `pipeline-${Date.now()}`,
      platform: formData.platform,
      contentType: formData.contentType,
      agentModel: formData.agentModel,
      manualIntervention: formData.manualIntervention,
      additionalPrompts: formData.additionalPrompts,
      time: formData.time,
      timezone: formData.timezone,
      frequency: formData.frequency,
      frequencyCount: formData.frequencyCount,
      temperature: formData.temperature[0],
      genre: formData.genre,
      topicType: formData.topicType,
      specificTopic: formData.specificTopic,
      regions: formData.regions,
      status: 'active',
      createdAt: new Date().toISOString(),

    // console.log('Pipeline data:', formData);
    // Handle pipeline creation
    // onOpenChange(false);
  };

  // Get existing pipelines from localStorage
    const existingPipelines = JSON.parse(localStorage.getItem('flowforge-pipelines') || '[]');

     // Add new pipeline
    const updatedPipelines = [...existingPipelines, pipeline];

    // Save to localStorage
    localStorage.setItem('flowforge-pipelines', JSON.stringify(updatedPipelines));

    console.log('Pipeline created:', pipeline);

    // Reset form
    setFormData({
      platform: '',
      contentType: '',
      agentModel: '',
      manualIntervention: false,
      additionalPrompts: '',
      time: '',
      timezone: '',
      frequency: 'weekly',
      frequencyCount: '1',
      temperature: [0.7],
      genre: 'All',
      topicType: '',
      specificTopic: '',
      regions: [],
    });

    // Notify parent component
    if (onPipelineCreated) {
      onPipelineCreated();
    }
    
    onOpenChange(false);
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
                  <TooltipContent className="bg-white text-black border">
                    <p>Choose where your content will be published</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <Select value={formData.platform} onValueChange={(value) => setFormData({...formData, platform: value})}>
              <SelectTrigger className="bg-white text-black border-gray-300">
                <SelectValue placeholder="Select platform" />
              </SelectTrigger>
              <SelectContent className="bg-white text-black">
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
              <SelectTrigger className="bg-white text-black border-gray-300">
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
                  <TooltipContent className="bg-white text-black border">
                    <p>AI model used to generate your content script</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </Label>
            <Select value={formData.agentModel} onValueChange={(value) => setFormData({...formData, agentModel: value})}>
              <SelectTrigger className="bg-white text-black border-gray-300">
                <SelectValue placeholder="Select AI model" />
              </SelectTrigger>
              <SelectContent className="bg-white text-black">
                {agentModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Manual Intervention */}
          <div className="space-y-2">
            <div className="flex items-center justify-between p-4 border border-gray-300 rounded-lg bg-gray-50">
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
            className="bg-white text-black border-gray-300"
              id="prompts"
              placeholder="Add specific instructions for content generation (e.g., tone, style, specific topics to cover...)"
              value={formData.additionalPrompts}
              onChange={(e) => setFormData({...formData, additionalPrompts: e.target.value})}
              rows={4}
            />
          </div>

          <Separator />

          {/* Time and Timezone */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="time" className="text-black">Posting Time</Label>
              <Input
              className={`bg-white border-gray-300 ${formData.time ? 'text-black' : 'text-gray-400'}`}
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
                <SelectTrigger className="bg-white text-black border-gray-300">
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
                <SelectTrigger className="bg-white text-black border-gray-300">
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
                className="bg-white text-black w-20 border-gray-300"
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
            <div className="p-4 border border-gray-300 rounded-lg bg-white text-gray-500">
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
              <SelectTrigger className="bg-white text-black border-gray-300">
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
              <SelectTrigger className="bg-white text-black border-gray-300">
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
            <div className="p-4 border border-gray-300 rounded-lg bg-gray-50 max-h-48 overflow-y-auto">
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
            <Button type="button" variant="outline" className="text-black border border-gray-300" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="bg-gradient-to-r from-purple-600 to-blue-600">
              <Sparkles className="size-4 mr-2" />
              Create Pipeline
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}