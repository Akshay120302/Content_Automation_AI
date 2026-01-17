import { Workflow, Wand2, Rocket, BarChart3, Bot, Zap, Shield, Clock } from "lucide-react";

const features = [
  {
    icon: Workflow,
    title: "Visual Workflow Builder",
    description: "Drag-and-drop interface to design complex automation flows without code",
  },
  {
    icon: Bot,
    title: "AI Agents",
    description: "Intelligent agents that understand context and create platform-optimized content",
  },
  {
    icon: Wand2,
    title: "Smart Templates",
    description: "Pre-built workflows for common content strategies that you can customize",
  },
  {
    icon: Rocket,
    title: "Auto-Publishing",
    description: "Schedule and publish content across all platforms automatically",
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "Track performance across all platforms in one unified view",
  },
  {
    icon: Zap,
    title: "Real-time Processing",
    description: "Generate and optimize content in seconds, not hours",
  },
  {
    icon: Shield,
    title: "Brand Consistency",
    description: "AI learns your brand voice and maintains it across all content",
  },
  {
    icon: Clock,
    title: "24/7 Automation",
    description: "Your content pipeline runs continuously without manual intervention",
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 relative bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-black">
            Powerful Features to{" "}
            <span className="text-gradient-molten">Supercharge</span> Your Content
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to build, automate, and scale your content 
            creation workflow.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="group p-6 rounded-2xl bg-card border border-gray-300 hover:border-forge-ember/30 transition-all duration-300 hover:translate-y-[-4px]"
              >
                <div className="mb-4 inline-flex p-3 rounded-xl bg-forge-ember/10 group-hover:bg-forge-ember/20 transition-colors duration-300">
                  <Icon className="h-6 w-6 text-forge-ember" />
                </div>
                <h3 className="font-display text-lg font-bold mb-2 text-foreground">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
