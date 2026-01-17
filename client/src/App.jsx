import { Toaster } from "./components/ui/toaster";
import { Toaster as Sonner } from "./components/ui/sonner.jsx";
import { TooltipProvider } from "./components/ui/tooltip.jsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import Index from "./pages/index";
import NotFound from "./pages/NotFound";
import { SignUp } from "./components/signup.jsx";
import { SignIn } from "./components/SignIn.jsx"
import { Dashboard } from "./components/Dashboard.jsx";  
import { PipelineDetailsView } from "./components/PipelineDetailsView.jsx";
import { Profile } from "./components/Profile.jsx";

const queryClient = new QueryClient();


const ProfileWrapper = () => {
  const navigate = useNavigate();
  return <Profile onNavigate={(page) => navigate(`/${page}`)} />;
};

const DashboardWrapper = () => {
  const navigate = useNavigate();
  return <Dashboard onNavigate={(page) => navigate(`/${page}`)} />;
};

const IndexWrapper = () => {
  const navigate = useNavigate();
  return <Index onNavigate={(page) => navigate(`/${page}`)} />;
};
const PipelineDetailWrapper = () => {
  const navigate = useNavigate();
  return <PipelineDetailsView onNavigate={(page) => navigate(`/${page}`)} />;
};
const SignUpWrapper = () => {
  const navigate = useNavigate();
  return <SignUp onNavigate={(page) => navigate(`/${page}`)} />;
};
const SignInWrapper = () => {
  const navigate = useNavigate();
  return <SignIn onNavigate={(page) => navigate(`/${page}`)} />;
};


const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<IndexWrapper />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
          <Route path="/signup" element={<SignUpWrapper />} />
          <Route path="/signin" element={<SignInWrapper />} />
          <Route path="/dashboard" element={<DashboardWrapper />} />
          <Route path="/profile" element={<ProfileWrapper  />} />
          <Route path="/pipeline/:pipelineId" element={<PipelineDetailWrapper />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
