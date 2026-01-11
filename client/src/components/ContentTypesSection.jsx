import { Video, Music, Image, FileText, Mic, Clapperboard } from "lucide-react";

const contentTypes = [
  {
    name: "Video",
    description: "Full videos, shorts, reels, and clips optimized for each platform",
    icon: Video,
    gradient: "from-red-500/20 to-orange-500/20",
  },
  {
    name: "Audio",
    description: "Podcasts, voiceovers, music, and audio content generation",
    icon: Music,
    gradient: "from-purple-500/20 to-pink-500/20",
  },
  {
    name: "Images",
    description: "Thumbnails, graphics, carousels, and visual content",
    icon: Image,
    gradient: "from-blue-500/20 to-cyan-500/20",
  },
  {
    name: "Text",
    description: "Articles, captions, scripts, and written content",
    icon: FileText,
    gradient: "from-green-500/20 to-emerald-500/20",
  },
  {
    name: "Voice",
    description: "AI voice cloning, text-to-speech, and narration",
    icon: Mic,
    gradient: "from-yellow-500/20 to-amber-500/20",
  },
  {
    name: "Stories",
    description: "Short-form narrative content for social platforms",
    icon: Clapperboard,
    gradient: "from-indigo-500/20 to-violet-500/20",
  },
];

const ContentTypesSection = () => {
  return (
    <section className="py-24 relative bg-card/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Create{" "}
            <span className="text-gradient-molten">Any Content</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From long-form videos to quick posts, FlowForge handles every content 
            format with AI-powered precision.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {contentTypes.map((type) => {
            const Icon = type.icon;
            return (
              <div
                key={type.name}
                className="group relative p-8 rounded-2xl bg-background border border-border hover:border-forge-ember/30 transition-all duration-300"
              >
                {/* Background gradient */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${type.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
                
                <div className="relative">
                  <div className="mb-4 inline-flex p-3 rounded-xl bg-secondary">
                    <Icon className="h-6 w-6 text-forge-ember" />
                  </div>
                  <h3 className="font-display text-xl font-bold mb-2 text-foreground">
                    {type.name}
                  </h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {type.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ContentTypesSection;
