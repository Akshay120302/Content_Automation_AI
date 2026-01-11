import { Youtube, Instagram, MessageSquare, FileText, Twitter, Linkedin, Music, Globe } from "lucide-react";

const platforms = [
  { name: "YouTube", icon: Youtube, color: "hover:text-red-500" },
  { name: "Instagram", icon: Instagram, color: "hover:text-pink-500" },
  { name: "Reddit", icon: MessageSquare, color: "hover:text-orange-500" },
  { name: "Medium", icon: FileText, color: "hover:text-foreground" },
  { name: "Twitter/X", icon: Twitter, color: "hover:text-sky-500" },
  { name: "LinkedIn", icon: Linkedin, color: "hover:text-blue-500" },
  { name: "TikTok", icon: Music, color: "hover:text-pink-400" },
  { name: "Blog", icon: Globe, color: "hover:text-green-500" },
];

const PlatformsSection = () => {
  return (
    <section id="platforms" className="py-24 relative">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            One Workflow.{" "}
            <span className="text-gradient-molten">Every Platform.</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Create once, distribute everywhere. FlowForge adapts your content 
            for each platform's unique requirements automatically.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {platforms.map((platform) => {
            const Icon = platform.icon;
            return (
              <div
                key={platform.name}
                className="group relative p-6 rounded-2xl bg-card border border-border hover:border-forge-ember/50 transition-all duration-300 hover:shadow-ember cursor-pointer"
              >
                <div className="flex flex-col items-center gap-4">
                  <div className="p-4 rounded-xl bg-secondary group-hover:bg-forge-ember/10 transition-colors duration-300">
                    <Icon className={`h-8 w-8 text-forge-steel transition-colors duration-300 ${platform.color}`} />
                  </div>
                  <span className="font-medium text-foreground">{platform.name}</span>
                </div>
                
                {/* Hover glow effect */}
                <div className="absolute inset-0 rounded-2xl bg-forge-ember/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl" />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default PlatformsSection;
