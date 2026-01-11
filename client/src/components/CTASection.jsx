import { Button } from "../components/ui/button";
import { ArrowRight, Flame } from "lucide-react";

const CTASection = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-forge-ember/10 rounded-full blur-[120px]" />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center justify-center p-4 rounded-2xl bg-forge-ember/10 mb-8">
            <Flame className="h-12 w-12 text-forge-ember glow-pulse" />
          </div>

          <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-bold mb-6">
            Ready to{" "}
            <span className="text-gradient-molten">Forge</span>{" "}
            Your Content Empire?
          </h2>

          <p className="text-lg text-muted-foreground mb-10 max-w-xl mx-auto">
            Join thousands of creators who are automating their content 
            production with FlowForge. Start free, scale infinitely.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button variant="forge" size="xl" className="group">
              Start Free Trial
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button variant="forgeOutline" size="xl">
              Schedule Demo
            </Button>
          </div>

          <p className="mt-6 text-sm text-muted-foreground">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
