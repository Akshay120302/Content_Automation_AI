import { Button } from "../components/ui/button";
import { ArrowRight, Sparkles, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-steel">
        {/* Molten glow effect */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-forge-ember/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-forge-flame/5 rounded-full blur-[100px]" />
        <div className="absolute top-1/3 right-1/4 w-[300px] h-[300px] bg-forge-molten/8 rounded-full blur-[80px]" />
        
        {/* Grid pattern overlay */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(hsl(var(--forge-steel)) 1px, transparent 1px),
                              linear-gradient(90deg, hsl(var(--forge-steel)) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary border border-gray-300 mb-8">
            <Sparkles className="h-4 w-4 text-forge-ember" />
            <span className="text-sm font-medium text-muted-foreground bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              AI-Powered Content Automation
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
            <span className="text-foreground font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Forge Your</span>
            <br />
            <span className="text-foreground font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Content Empire</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            Build fully automated AI workflows that create stunning content for 
            YouTube, Instagram, Reddit, Medium and more. One workflow, endless possibilities.
          </p>

          {/* CTA Buttons */}
         <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link to="/signin">
            <Button variant="forge" size="xl" className="group bg-gradient-molten">
              Start Forging
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            </Link>
            <Button variant="forgeOutline" size="xl">
              <Zap className="h-5 w-5" />
              Watch Demo
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-10 border-t border-gray-300">
            {[
              { value: "10+", label: "Platforms" },
              { value: "50+", label: "AI Actions" },
              { value: "100%", label: "Automated" },
              { value: "24/7", label: "Running" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="font-display text-3xl sm:text-4xl font-bold text-purple-600 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
};

export default HeroSection;
