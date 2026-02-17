import { useState } from "react";
import { Link } from "react-router-dom"; 
import { DashboardLayout } from "@/components/layout/DashboardLayout";            
import { GeneratorForm } from "@/components/generators/GeneratorForm";            
import { OutputDisplay } from "@/components/generators/OutputDisplay";            
import { GenerationLimitModal } from "@/components/generators/GenerationLimitModal";                                       
import { Button } from "@/components/ui/button";                                  
import { ArrowLeft, MessageCircle } from "lucide-react";                          
import { toast } from "@/hooks/use-toast";
import { generatorService } from "@/lib/api";                                     

const BellRinger = () => {
  const [learningGoal, setLearningGoal] = useState("");
  const [gradeLevel, setGradeLevel] = useState("high");
  const [isLoading, setIsLoading] = useState(false);                                
  const [output, setOutput] = useState<{ 
    title: string; 
    icon: string; 
    content: string 
  }[]>([]);                                                                        
  const [isFavorited, setIsFavorited] = useState(false);                            
  const [showLimitModal, setShowLimitModal] = useState(false);                      
  const [contentId, setContentId] = useState<number | undefined>();                 
  const [docxUrl, setDocxUrl] = useState<string | undefined>();                     
  const [pdfUrl, setPdfUrl] = useState<string | undefined>();                     

  const handleGenerate = async () => {   
    if (!learningGoal.trim()) {
      toast({
        title: "Topic required",
        description: "Please describe the concept students are ready to think more deeply about.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setOutput([]);
    setIsFavorited(false);

    try {
      const response = await generatorService.generateDiscussionQuestions({
        grade_level: gradeLevel,
        topic: learningGoal,
        subject: "Food Science",
      });

      const content = typeof response.content === 'string' ? response.content : (response.content ? String(response.content) : '');
      
      const formattedOutput = [{
        title: "DISCUSSION QUESTIONS",
        icon: "❓",
        content: content
      }];

      setOutput(formattedOutput);
      setContentId(response.id);
      setDocxUrl(response.formatted_docx_url);
      setPdfUrl(response.formatted_pdf_url);
    } catch (error: any) {
      console.error('Generation error:', error);
      
      let errorMessage = "Failed to generate discussion questions. Please try again.";
      
      // Check if it's an API error with response data
      if (error?.response?.data?.error) {
        errorMessage = error.response.data.error;
        
        // Check for generation limit error specifically
        if (error.response.data.error_type === 'generation_limit_reached') {
          setShowLimitModal(true);
          return;
        }
      } else if (error?.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Generation failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = () => {       
    handleGenerate();
  };

  const handleSave = async () => {       
    if (output.length === 0) {
      toast({
        title: "No content to save",     
        description: "Please generate content first.",                                    
        variant: "destructive",
      });
      return;
    }

    // Content is automatically saved when generated                                  
    toast({
      title: "Saved to library",
      description: "Discussion questions have been saved to your history.",           
    });
  };

  const handleFavorite = async () => {   
    if (!contentId) {
      toast({
        title: "Cannot favorite",        
        description: "Content must be generated and saved first.",                        
        variant: "destructive",
      });
      return;
    }

    try {
      console.log('Toggling favorite for contentId:', contentId);                       
      const result = await generatorService.toggleFavorite(contentId);                  
      console.log('Favorite toggle result:', result);                                   
      setIsFavorited(result.is_favorite);
      toast({
        title: result.is_favorite ? "Added to favorites" : "Removed from favorites",                                               
        description: result.message,     
      });
    } catch (error: any) {
      console.error('Error toggling favorite:', error);
      console.error('Error response:', error?.response);
      const errorMessage = error?.response?.data?.error || error?.response?.data?.message || error?.message || "Could not update favorite status. Please try again.";
      toast({
        title: "Failed to update favorite",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">        
        {/* Header */}
        <div className="flex items-center gap-4">                                           
          <Button variant="ghost" size="sm" asChild>                                          
            <Link to="/dashboard">       
              <ArrowLeft className="w-4 h-4 mr-1" />                                            
              Back to Dashboard
            </Link>
          </Button>
        </div>

        <div className="animate-fade-in">
          <h1 className="font-serif text-2xl md:text-3xl font-bold text-foreground mb-2 flex items-center gap-3">                      
            <MessageCircle className="w-8 h-8 text-primary" />                                
            Discussion Questions Generator                                                  
          </h1>
          <p className="text-muted-foreground">                                               
            Generate concept-deepening discussion questions grounded in real food situations — reasoning, evidence, tradeoffs, and decision-making.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-2">                                         
          <div className="animate-slide-up" style={{ animationDelay: "100ms" }}>              
            <GeneratorForm
            title="What concept are students ready to think more deeply about?"
            description="Describe the idea you just taught and how students should reason about it in real food situations."
            icon={<MessageCircle className="w-5 h-5 text-primary" />}                         
            learningGoal={learningGoal}
            onLearningGoalChange={setLearningGoal}
            learningGoalPlaceholder="Example: Evaluate how storage decisions affect food safety and quality in a school cafeteria."
            gradeLevel={gradeLevel}    
            onGradeLevelChange={setGradeLevel}                                                
            onSubmit={handleGenerate}  
            isLoading={isLoading}
            submitLabel="Generate Discussion Questions"
            >
            </GeneratorForm>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "200ms" }}>              
            <OutputDisplay
              sections={output}
              isLoading={isLoading}      
              onRegenerate={handleRegenerate}                                                   
              onSave={handleSave}        
              onFavorite={handleFavorite}
              isFavorited={isFavorited}  
              contentId={contentId}      
              docxUrl={docxUrl}
              pdfUrl={pdfUrl}
            />
          </div>
        </div>
      </div>
      <GenerationLimitModal open={showLimitModal} onOpenChange={setShowLimitModal} />                                          
    </DashboardLayout>
  );
};

export default BellRinger;