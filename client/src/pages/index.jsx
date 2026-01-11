import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import PlatformsSection from "../components/PlatformsSection";
import ContentTypesSection from "../components/ContentTypesSection";
import FeaturesSection from "../components/FeaturesSection";
import HowItWorksSection from "../components/HowItWorksSection";
import CTASection from "../components/CTASection";
import Footer from "../components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      <PlatformsSection />
      <ContentTypesSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;
