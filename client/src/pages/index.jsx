import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import PlatformsSection from "../components/PlatformsSection";
import ContentTypesSection from "../components/ContentTypesSection";
import FeaturesSection from "../components/FeaturesSection";
import HowItWorksSection from "../components/HowItWorksSection";
import { Pricing } from "../components/Pricing";
import CTASection from "../components/CTASection";
import Footer from "../components/Footer";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      <PlatformsSection />
      <ContentTypesSection />
      <FeaturesSection />
      <HowItWorksSection />
      <Pricing onNavigate={(page) => navigate(`/${page}`)} />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;
