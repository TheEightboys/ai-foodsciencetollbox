import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/auth/AuthModal";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import logo from "@/assets/logo.png";
export default function About() {
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="gradient-primary text-white py-4 sticky top-0 z-50 shadow-lg">
        <nav className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <img src={logo} alt="Food Science Toolbox" className="w-10 h-10 object-contain" />
              <span className="text-xl font-semibold">AI Teaching Assistant</span>
            </div>
            <ul className="hidden md:flex items-center gap-8 list-none">
              <li><Link to="/#features" className="text-white hover:opacity-80 transition-opacity">Features</Link></li>
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

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="space-y-8">
          <div>
            <h1 className="text-4xl font-bold mb-4">About</h1>
            <p className="text-lg text-muted-foreground mb-6">
              This AI teaching tool was created by Dr. Courtney Simons, founder of Food Science Toolbox, an educational platform dedicated to helping teachers deliver high-quality, classroom-ready instruction with confidence.
            </p>
            <p className="text-muted-foreground mb-6">
              Dr. Simons is a food scientist and educator with experience teaching at both the vocational and college levels. Through years of classroom instruction and direct teacher support, Dr. Simons has worked closely with educators who are often asked to teach complex scientific concepts with limited preparation time and, in many cases, outside their original training area.
            </p>
            <p className="text-muted-foreground">
              Across these settings, one challenge has remained consistent. Teachers invest significant time developing lesson materials, yet still question whether those materials are instructionally sound, appropriately leveled, and truly ready for students. This AI teaching tool was created to address that challenge directly.
            </p>
          </div>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">The Reality of Most AI Tools</h2>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">AI tools are prompt dependent.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Better prompts lead to better results.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Teachers must figure out how to ask the right way.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">AI typically generates plain text. Formatting is left to the teacher.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Time saved generating content is often lost editing and formatting.</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">How This Tool Is Different</h2>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">Prompts are embedded and tested.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">No prompt engineering required.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">Outputs are structured and consistent.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">Materials are pre-formatted and classroom ready.</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">Why It Matters</h2>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">Less time planning.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">Less time formatting.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                  <span className="text-muted-foreground">More time teaching.</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">Who This Tool Is For</h2>
              <p className="text-muted-foreground mb-4">
                This tool is designed for educators who value structure, clarity, and instructional accuracy.
              </p>
              <p className="text-muted-foreground mb-4">It is particularly useful for:</p>
              <ul className="space-y-2">
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Elementary, middle, and high school teachers</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Vocational and technical education instructors</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">College instructors teaching applied science or introductory courses</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Teachers working outside their primary content area</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground">Educators seeking classroom-ready materials they can use immediately</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">About Food Science Toolbox</h2>
              <p className="text-muted-foreground mb-4">
                Food Science Toolbox is an educational resource hub created to support teachers in food science, family and consumer sciences, and related disciplines. The platform provides ready-to-use teaching materials, instructional guidance, and tools that help educators bring applied science into the classroom in practical and engaging ways.
              </p>
              <p className="text-muted-foreground">
                This AI teaching tool is an extension of the Food Science Toolbox mission: to make strong instruction more accessible and less time-consuming, especially for educators working in applied and vocational education settings.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-12 mt-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <img src={logo} alt="AI Teaching Assistant" className="w-10 h-10 object-contain" />
                <span className="text-xl font-semibold text-white">AI Teaching Assistant</span>
              </div>
              <p className="text-gray-400 leading-relaxed max-w-md">
                Empowering educators with AI-powered tools to create engaging, high-quality educational content in minutes.
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
                <li><Link to="/#features" className="text-gray-400 hover:text-white transition-colors">Features</Link></li>
                <li><Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              &copy; {new Date().getFullYear()} AI Teaching Assistant. All rights reserved.
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
}

