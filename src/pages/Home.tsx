import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Sparkles, 
  BookOpen, 
  Target,
  MessageSquare,
  ArrowRight,
  CheckCircle2
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/auth/AuthModal";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";

const Home = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Redirect to dashboard when user logs in via modal
  useEffect(() => {
    if (user && showAuthModal) {
      setShowAuthModal(false);
      navigate("/dashboard");
    }
  }, [user, showAuthModal, navigate]);

  // Redirect authenticated users to dashboard if they visit homepage
  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="gradient-primary text-white py-4 sticky top-0 z-50 shadow-lg">
        <nav className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-xl font-semibold">Food Science Toolbox Teaching Assistant</span>
            </div>
            <ul className="hidden md:flex items-center gap-8 list-none">
              <li><Link to="/about" className="text-white hover:opacity-80 transition-opacity">About</Link></li>
              <li><a href="https://foodsciencetoolbox.com/cat/articles/" target="_blank" rel="noopener noreferrer" className="text-white hover:opacity-80 transition-opacity">Blog</a></li>
              <li><Link to="/account/contact" className="text-white hover:opacity-80 transition-opacity">Contact</Link></li>
            </ul>
            <div className="flex items-center gap-4">
              {user ? (
                <Button asChild variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Link to="/dashboard">Dashboard</Link>
                </Button>
              ) : (
                <>
                  <Button 
                    variant="ghost"
                    className="text-white hover:bg-white/10"
                    onClick={() => setShowAuthModal(true)}
                  >
                    Log In
                  </Button>
                  <Button 
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-full px-6"
                    onClick={() => setShowAuthModal(true)}
                  >
                    Get Started
                  </Button>
                </>
              )}
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24 md:py-32">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-500/20 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-emerald-500/20 via-transparent to-transparent"></div>
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:50px_50px]"></div>
        
        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8 max-w-2xl">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-sm font-medium">
                <Sparkles className="w-4 h-4 text-green-400" />
                <span>Specialized for Food Science Education</span>
              </div>
              
              {/* Main heading */}
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight tracking-tight">
                Transform Your
                <span className="block bg-gradient-to-r from-green-400 via-emerald-400 to-green-500 bg-clip-text text-transparent">
                  Food Science Teaching
                </span>
              </h1>
              
              {/* Description */}
              <p className="text-xl md:text-2xl text-gray-300 leading-relaxed">
                Create engaging food science lesson plans, nutrition activities, and culinary education content in seconds with your Teaching Assistant designed exclusively for food science educators.
              </p>
              
              {/* CTA buttons */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <Button 
                  size="lg" 
                  className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold text-lg px-8 py-6 rounded-xl shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 group"
                  onClick={() => user ? navigate("/dashboard") : setShowAuthModal(true)}
                >
                  Start Creating Free
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                  <span>No credit card required</span>
                </div>
              </div>
            </div>
            
            {/* Hero image */}
            <div className="relative hidden lg:block">
              <div className="relative z-10">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-3xl blur-2xl opacity-20"></div>
                <img 
                  src="/images.png" 
                  alt="Teacher helping students in a food science classroom" 
                  className="relative rounded-3xl shadow-2xl object-contain w-full max-h-[560px] transform hover:scale-[1.02] transition-transform duration-500" 
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 md:py-32 bg-gradient-to-b from-background via-slate-50 to-background dark:from-background dark:via-slate-900 dark:to-background">
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-primary">Powerful Features</span>
            </div>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6">
              Everything You Need for
              <span className="block bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">Food Science Education</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Save hours every week with AI-powered tools designed specifically for food science and consumer science educators.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="group relative overflow-hidden border-2 hover:border-primary/50 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 bg-gradient-to-br from-white to-gray-50 dark:from-slate-900 dark:to-slate-800">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <CardContent className="p-8 relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <BookOpen className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-foreground">Lesson Starter Generator</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  Create engaging food science lesson openers covering nutrition, food chemistry, culinary techniques, and food safety topics.
                </p>
                <Link to="/dashboard" className="inline-flex items-center gap-2 text-primary hover:gap-3 font-semibold text-sm transition-all group/link">
                  Explore <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>
            <Card className="group relative overflow-hidden border-2 hover:border-primary/50 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 bg-gradient-to-br from-white to-gray-50 dark:from-slate-900 dark:to-slate-800">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <CardContent className="p-8 relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Target className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-foreground">Learning Objectives Generator</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  Generate measurable, grade-appropriate learning objectives aligned with food science and nutrition education standards.
                </p>
                <Link to="/dashboard" className="inline-flex items-center gap-2 text-primary hover:gap-3 font-semibold text-sm transition-all group/link">
                  Explore <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>
            <Card className="group relative overflow-hidden border-2 hover:border-primary/50 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 bg-gradient-to-br from-white to-gray-50 dark:from-slate-900 dark:to-slate-800">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <CardContent className="p-8 relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-bold text-xl mb-3 text-foreground">Discussion Questions Generator</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  Build thought-provoking food science discussion questions that promote critical thinking about nutrition, cooking, and food systems.
                </p>
                <Link to="/dashboard" className="inline-flex items-center gap-2 text-primary hover:gap-3 font-semibold text-sm transition-all group/link">
                  Explore <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>

          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 md:py-32 bg-gradient-to-b from-background to-slate-50 dark:to-slate-900 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-blue-500/5 to-emerald-500/5 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-primary">Simple Process</span>
            </div>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6">
              Get Started in
              <span className="block bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">Three Easy Steps</span>
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <Card className="relative bg-white dark:bg-slate-900 border-2 hover:border-blue-500/50 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="flex items-start gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
                        <span className="text-2xl font-bold text-white">1</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-xl mb-3 text-foreground">Choose Your Tool</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Select from our comprehensive suite of AI-powered food science teaching tools - from nutrition lessons to culinary labs.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <Card className="relative bg-white dark:bg-slate-900 border-2 hover:border-blue-500/50 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="flex items-start gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
                        <span className="text-2xl font-bold text-white">2</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-xl mb-3 text-foreground">Customize Settings</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Tailor food science content to your curriculum with customizable parameters for nutrition, culinary arts, and food safety topics.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <Card className="relative bg-white dark:bg-slate-900 border-2 hover:border-green-500/50 transition-all duration-300">
                <CardContent className="p-8">
                  <div className="flex items-start gap-6">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
                        <span className="text-2xl font-bold text-white">3</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-xl mb-3 text-foreground">Generate & Use</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Get professional-quality content instantly, ready to use in your classroom or share with students.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
          <div className="text-center mt-16">
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-700 hover:to-emerald-700 text-white font-semibold px-10 py-6 rounded-xl shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 group"
              onClick={() => user ? navigate("/dashboard") : setShowAuthModal(true)}
            >
              Start Creating Now
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white py-24 md:py-32">
        {/* Animated background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-600/20 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:50px_50px]"></div>
        
        {/* Decorative blurs */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span>Start Your Free Trial</span>
            </div>
            
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
              Ready to Transform Your
              <span className="block bg-gradient-to-r from-green-400 via-emerald-400 to-green-500 bg-clip-text text-transparent">
                Food Science Classroom?
              </span>
            </h2>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-10 leading-relaxed max-w-2xl mx-auto">
              Join food science educators who are saving time and creating better curriculum-aligned content with specialized AI tools.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold text-lg px-10 py-7 rounded-xl shadow-2xl hover:shadow-3xl hover:-translate-y-1 transition-all duration-300 group"
                onClick={() => user ? navigate("/dashboard") : setShowAuthModal(true)}
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>No credit card • Free forever plan</span>
              </div>
            </div>
            
            {/* Trust indicators */}
            <div className="flex items-center justify-center gap-8 pt-8 border-t border-white/10">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Instant Access</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Cancel Anytime</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Free Support</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-xl font-semibold text-white">Food Science Toolbox Teaching Assistant</span>
              </div>
              <p className="text-gray-400 leading-relaxed max-w-md">
                Empowering food science educators with specialized AI-powered tools to create engaging, curriculum-aligned content for nutrition, culinary arts, food chemistry, and food safety education.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Quick Links</h4>
              <ul className="space-y-2">
                <li><Link to="/about" className="text-gray-400 hover:text-white transition-colors">About</Link></li>
                <li><a href="https://foodsciencetoolbox.com/cat/articles/" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
                <li><Link to="/account/contact" className="text-gray-400 hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              &copy; {new Date().getFullYear()} Food Science Toolbox Teaching Assistant. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <Dialog open={showAuthModal} onOpenChange={setShowAuthModal}>
        <DialogContent className="max-w-md p-0 border-0">
          <DialogTitle className="sr-only">Sign in to Food Science Toolbox</DialogTitle>
          <AuthModal onClose={() => setShowAuthModal(false)} />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Home;
