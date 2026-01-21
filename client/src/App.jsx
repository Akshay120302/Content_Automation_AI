import { Toaster } from "./components/ui/toaster";
import { Toaster as Sonner } from "./components/ui/sonner.jsx";
import { TooltipProvider } from "./components/ui/tooltip.jsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from "react-router-dom";
import Index from "./pages/index";
import NotFound from "./pages/NotFound";
import { SignUp } from "./components/SignUp.jsx";
import { SignIn } from "./components/SignIn.jsx"
import { Dashboard } from "./components/Dashboard.jsx";  
import { PipelineDetailsView } from "./components/PipelineDetailsView.jsx";
import { Profile } from "./components/Profile.jsx";
import { SubscriptionPage } from "./components/SubscriptionPage.jsx";
import { ContentEditor } from "./components/ContentEditor.jsx";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { GuestRoute } from "./components/GuestRoute";

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

// Main router component (must be inside BrowserRouter)
const AppRoutes = () => {
  const SubscriptionWrapper = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const selectedPlan = searchParams.get('plan') || 'Pro';
    return <SubscriptionPage onNavigate={(page) => navigate(`/${page}`)} selectedPlan={selectedPlan} />;
  };

  const ContentEditorWrapper = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const queueItem = {
      id: searchParams.get('id') || '1',
      type: searchParams.get('type') || 'video',
      platform: searchParams.get('platform') || 'YouTube',
      status: searchParams.get('status') || 'generating',
    };
    return <ContentEditor onNavigate={(page) => navigate(`/${page}`)} queueItem={queueItem} />;
  };

  return (
    <Routes>
            <Route path="/" element={<IndexWrapper />} />
            <Route 
              path="/signup" 
              element={
                <GuestRoute>
                  <SignUpWrapper />
                </GuestRoute>
              } 
            />
            <Route 
              path="/signin" 
              element={
                <GuestRoute>
                  <SignInWrapper />
                </GuestRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardWrapper />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfileWrapper />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/subscription" 
              element={
                <ProtectedRoute>
                  <SubscriptionWrapper />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/pipeline/:pipelineId" 
              element={
                <ProtectedRoute>
                  <PipelineDetailWrapper />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/content-editor" 
              element={
                <ProtectedRoute>
                  <ContentEditorWrapper />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
