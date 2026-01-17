import { Button } from "../components/ui/button";
import Logo from "@/components/Logo";
import { Menu, X, ArrowLeft, CreditCard, User, Zap } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";

const Navbar = ({ variant = "default", onNavigate, userData, backTarget }) => {
  const [isOpen, setIsOpen] = useState(false);

  // ---------------- PROFILE/Dashboard/pipeline/etc NAVBAR ----------------
  if (variant === "profile") {
    return (
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* <Button
                variant="ghost"
                size="sm"
                
              >
                <ArrowLeft className="size-4 mr-2" />
              </Button> */}

              <button
                onClick={() => onNavigate?.("")}
                className="flex items-center gap-2 cursor-pointer"
              >
                <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
                  <Zap className="size-5 text-white" fill="currentColor" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  FlowForge
                </span>
              </button>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-purple-50 rounded-lg border border-purple-200">
                <CreditCard className="size-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-700">
                  {userData?.subscription?.plan}
                </span>
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-10 w-10 rounded-full"
                  >
                    <Avatar>
                      <AvatarImage
                        src={userData?.avatar}
                        alt={userData?.name}
                      />
                      <AvatarFallback className="bg-gradient-to-br from-purple-600 to-blue-600 text-white">
                        {userData?.initials}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-white">
                  <DropdownMenuLabel>
                    <div className="flex flex-col">
                      <span className="font-semibold">{userData?.name}</span>
                      <span className="text-xs text-gray-500">
                        {userData?.email}
                      </span>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => onNavigate?.("profile")}>
                    <User className="size-4 mr-2" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onNavigate?.("home")}>
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  // ---------------- DEFAULT (HOME) NAVBAR ----------------
  const navLinks = [
    { label: "Features", href: "#features" },
    { label: "Platforms", href: "#platforms" },
    { label: "How it Works", href: "#how-it-works" },
    { label: "Pricing", href: "#pricing" },
    { label: "Dashboard", href: "/dashboard" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-b border-gray-300">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Logo />

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200"
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link to="/signin">
              <Button variant="forge" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/signup">
              <Button variant="forge" size="sm">
                Get Started
              </Button>
            </Link>
          </div>

          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {isOpen && (
          <div className="md:hidden py-4 border-t border-gray-300">
            <div className="flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-2"
                  onClick={() => setIsOpen(false)}
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
