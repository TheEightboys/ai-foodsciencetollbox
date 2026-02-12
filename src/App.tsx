/**
 * Main Application Component
 * 
 * Sets up the application's provider hierarchy and routing configuration.
 * This component wraps the entire application with necessary context providers
 * and defines all application routes.
 */

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

// Page imports
import Home from "./pages/Home";
import Index from "./pages/Index";
import Pricing from "./pages/Pricing";
import LessonStarter from "./pages/LessonStarter";
import LearningObjectives from "./pages/LearningObjectives";
import BellRinger from "./pages/BellRinger";

import History from "./pages/History";
import ComingSoon from "./pages/ComingSoon";
import NotFound from "./pages/NotFound";
import ProfileSettings from "./pages/account/ProfileSettings";
import Billing from "./pages/account/Billing";
import HelpSupport from "./pages/account/HelpSupport";
import ContactSupport from "./pages/account/ContactSupport";
import About from "./pages/About";
import LegalDocument from "./pages/legal/LegalDocument";
import GoogleCallback from "./pages/auth/GoogleCallback";
import VerifyEmail from "./pages/auth/VerifyEmail";
import ResetPassword from "./pages/auth/ResetPassword";

/**
 * React Query client configuration.
 * Provides default options for data fetching and caching.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public homepage - default landing page */}
              <Route path="/" element={<Home />} />
              {/* Dashboard - protected route */}
              <Route path="/dashboard" element={<ProtectedRoute><Index /></ProtectedRoute>} />
              <Route path="/pricing" element={<ProtectedRoute><Pricing /></ProtectedRoute>} />
              <Route path="/lesson-starter" element={<ProtectedRoute><LessonStarter /></ProtectedRoute>} />
              <Route path="/objectives" element={<ProtectedRoute><LearningObjectives /></ProtectedRoute>} />
              
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              
              {/* Account Pages */}
              <Route path="/account/profile" element={<ProtectedRoute><ProfileSettings /></ProtectedRoute>} />
              <Route path="/account/billing" element={<ProtectedRoute><Billing /></ProtectedRoute>} />
              <Route path="/account/help" element={<ProtectedRoute><HelpSupport /></ProtectedRoute>} />
              <Route path="/account/contact" element={<ProtectedRoute><ContactSupport /></ProtectedRoute>} />
              <Route path="/about" element={<About />} />
              
              {/* Auth Callbacks - Public routes */}
              <Route path="/auth/google/callback" element={<GoogleCallback />} />
              <Route path="/verify-email/:token" element={<VerifyEmail />} />
              <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />
              
              {/* Legal Documents - Public routes */}
              <Route path="/legal/:documentType" element={<LegalDocument />} />
              <Route path="/terms" element={<LegalDocument />} />
              <Route path="/privacy" element={<LegalDocument />} />
              <Route path="/acceptable-use" element={<LegalDocument />} />
              
              {/* Starter Plan Generators */}
              <Route path="/lesson-plan" element={<ProtectedRoute><ComingSoon title="Lesson Plan Generator" description="Build structured lesson plans that outline objectives, activities, and assessments in one place." /></ProtectedRoute>} />
              <Route path="/quiz" element={<ProtectedRoute><ComingSoon title="Multiple Choice Quiz Generator" description="Generate ready-to-use multiple choice questions aligned with your lesson content." /></ProtectedRoute>} />
              <Route path="/key-terms" element={<ProtectedRoute><ComingSoon title="Key Terms and Definitions Generator" description="Create student-friendly vocabulary lists with clear definitions for your topic." /></ProtectedRoute>} />
              <Route path="/check-in" element={<ProtectedRoute><BellRinger /></ProtectedRoute>} />
              
              {/* Pro Plan Generators */}
              <Route path="/required-reading" element={<ProtectedRoute><ComingSoon title="Required Reading Generator" description="Generate structured reading content students can review to understand key concepts." /></ProtectedRoute>} />
              <Route path="/slides" element={<ProtectedRoute><ComingSoon title="Slide Generator" description="Create slide-ready content with clear headings and key points for presentations." /></ProtectedRoute>} />
              <Route path="/worksheet" element={<ProtectedRoute><ComingSoon title="Worksheet Generator" description="Generate printable worksheets that help students practice and apply concepts." /></ProtectedRoute>} />
              <Route path="/rubric" element={<ProtectedRoute><ComingSoon title="Rubric Generator" description="Build clear grading rubrics with defined criteria and performance levels." /></ProtectedRoute>} />
              <Route path="/lab" element={<ProtectedRoute><ComingSoon title="Food Science Laboratory Generator" description="Create classroom-appropriate food science lab activities with objectives and procedures." /></ProtectedRoute>} />
              <Route path="/image-generator" element={<ProtectedRoute><ComingSoon title="Image Generator" description="Generate educational visuals to support explanations and student understanding." /></ProtectedRoute>} />
              <Route path="/project-ideas" element={<ProtectedRoute><ComingSoon title="Project Ideas Generator" description="Generate student project ideas aligned to food science and consumer science topics." /></ProtectedRoute>} />
              <Route path="/project-proposal" element={<ProtectedRoute><ComingSoon title="Project Proposal Generator" description="Create structured project proposal templates students can use to plan their work." /></ProtectedRoute>} />
              <Route path="/recipe" element={<ProtectedRoute><ComingSoon title="Recipe Generator" description="Generate instructional recipes designed for classroom use and concept demonstration." /></ProtectedRoute>} />
              <Route path="/nutrition-label" element={<ProtectedRoute><ComingSoon title="Nutrition Label Generator" description="Create Nutrition Facts style labels based on ingredients or recipes for instructional use." /></ProtectedRoute>} />
              <Route path="/teacher-jokes" element={<ProtectedRoute><ComingSoon title="Teacher Jokes Generator" description="Generate light, classroom-appropriate humor related to food science topics." /></ProtectedRoute>} />
              <Route path="/ask-courtney" element={<ProtectedRoute><ComingSoon title="Ask Courtney" description="Ask food science questions and receive clear, classroom-ready explanations." /></ProtectedRoute>} />
              
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
