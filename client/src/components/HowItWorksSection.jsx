import { Lightbulb, Cpu, Send, TrendingUp } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Lightbulb,
    title: "Define Your Strategy",
    description: "Set your content goals, target audience, and brand voice. Our AI learns your unique style.",
  },
  {
    number: "02",
    icon: Cpu,
    title: "Build Your Workflow",
    description: "Use our visual builder to connect AI agents, content generators, and publishing nodes.",
  },
  {
    number: "03",
    icon: Send,
    title: "Automate & Publish",
    description: "Your workflow runs on autopilot, creating and publishing content 24/7 across platforms.",
  },
  {
    number: "04",
    icon: TrendingUp,
    title: "Optimize & Scale",
    description: "AI analyzes performance and continuously improves your content for better engagement.",
  },
];

const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="py-24 relative bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-bold mb-4 text-black">
            How{" "}
            <span className="text-gradient-molten">FlowForge</span>{" "}
            Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From idea to published content in four simple steps
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto">
          {/* Connection line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-forge-ember/30 to-transparent -translate-y-1/2" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={step.number} className="relative">
                  <div className="group text-center">
                    {/* Step number */}
                    <div className="relative inline-flex mb-6">
                      <div className="w-20 h-20 rounded-2xl bg-background border-2 border-gray-500 flex items-center justify-center group-hover:border-forge-ember group-hover:shadow-ember transition-all duration-300">
                        <Icon className="h-8 w-8 text-forge-ember" />
                      </div>
                      <span className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-molten flex items-center justify-center text-xs font-bold text-primary-foreground">
                        {step.number}
                      </span>
                    </div>

                    <h3 className="font-display text-xl font-bold mb-3 text-foreground">
                      {step.title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
