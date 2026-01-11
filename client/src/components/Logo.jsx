import { Flame } from "lucide-react";
import { Link } from "react-router-dom";

const Logo = () => {
  return (
    <Link to="/" className="flex items-center gap-2 group">
      <div className="relative">
        <Flame className="h-8 w-8 text-forge-ember glow-pulse" />
        <div className="absolute inset-0 bg-forge-ember/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      <span className="font-display text-xl font-bold text-gradient-molten">
        FlowForge
      </span>
    </Link>
  );
};

export default Logo;
