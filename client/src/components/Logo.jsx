import { Flame } from "lucide-react";
import { Link } from "react-router-dom";

const Logo = () => {
  return (
    <Link to="/" className="flex items-center gap-2 group">
      <div className="relative">
        <Flame className="h-8 w-8 text-forge-ember glow-pulse" />
        <div className="absolute inset-0 bg-forge-ember/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
      <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
        FlowForge
      </span>
    </Link>
  );
};

export default Logo;
