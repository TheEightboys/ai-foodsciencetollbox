import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { GeneratorForm } from "@/components/generators/GeneratorForm";
import { OutputDisplay } from "@/components/generators/OutputDisplay";
import { GenerationLimitModal } from "@/components/generators/GenerationLimitModal";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Target } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { generatorService } from "@/lib/api";
import { formatContentWithMetadata } from "@/lib/utils/contentFormatter";

const LearningObjectives = () => {
  const [userIntent, setUserIntent] = useState("");
  const [gradeLevel, setGradeLevel] = useState("high");
  const [numObjectives, setNumObjectives] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [output, setOutput] = useState<{ title: string; icon: string; content: string }[]>([]);
  const [isFavorited, setIsFavorited] = useState(false);
  const [showLimitModal, setShowLimitModal] = useState(false);
  const [contentId, setContentId] = useState<number | undefined>();
  const [docxUrl, setDocxUrl] = useState<string | undefined>();
  const [pdfUrl, setPdfUrl] = useState<string | undefined>();
  const [routingInfo, setRoutingInfo] = useState<any>(null);
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [warnings, setWarnings] = useState<string[]>([]);

  const handleGenerate = async () => {
    if (!userIntent.trim()) {
      toast({
        title: "Learning intent required",
        description: "Please describe what you want students to learn or be able to do.",
        variant: "destructive",
      });
      return;
    }

    if (userIntent.trim().length < 10) {
      toast({
        title: "Learning intent too short",
        description: "Please provide more detail about what you want students to learn (minimum 10 characters).",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setOutput([]);
    setIsFavorited(false);
    setRoutingInfo(null);
    setQualityMetrics(null);
    setWarnings([]);

    try {
      const response = await generatorService.generateLearningObjectives({
        user_intent: userIntent,
        grade_level: gradeLevel.charAt(0).toUpperCase() + gradeLevel.slice(1), // Capitalize first letter
        num_objectives: numObjectives,
      });

      const formattedContent = formatContentWithMetadata(
        response.content,
        gradeLevel,
        userIntent
      );
      setOutput([
        {
          title: "LEARNING OBJECTIVES",
          icon: "🎯",
          content: formattedContent,
        },
      ]);

      if (response.routing_info) {
        setRoutingInfo(response.routing_info);
      }
      if (response.quality_metrics) {
        setQualityMetrics(response.quality_metrics);
      }
      if (response.warnings) {
        setWarnings(response.warnings);
      }

      if (response.id) {
        setContentId(response.id);
        try {
          const allContent = await generatorService.listGeneratedContent();
          const thisContent = allContent.find(c => c.id === response.id);
          setIsFavorited(thisContent?.is_favorite || false);
        } catch (error) {
          setIsFavorited(false);
        }
        let apiBaseUrl = response.formatted_docx_url 
          ? response.formatted_docx_url.replace(/\/generators\/\d+\/export\/docx\/$/, '')
          : (import.meta.env.VITE_API_BASE_URL || 
             (typeof window !== 'undefined' ? window.location.origin : ''));
        
        if (!apiBaseUrl.endsWith('/api')) {
          apiBaseUrl = apiBaseUrl.replace(/\/api\/?$/, '') + '/api';
        }
        
        setDocxUrl(`${apiBaseUrl}/generators/${response.id}/export/docx/`);
        setPdfUrl(`${apiBaseUrl}/generators/${response.id}/export/pdf/`);
      }
      toast({
        title: "Objectives generated!",
        description: `Learning objectives are ready${response.routing_info?.domain ? ` for ${response.routing_info.domain_description}` : ''}.`,
      });
    } catch (error: any) {
      if (error.response?.status === 403 && error.response?.data?.error_type === 'generation_limit_reached') {
        setShowLimitModal(true);
      } else {
        toast({
          title: "Generation failed",
          description: error.response?.data?.error || error.response?.data?.detail || error.message || "Failed to generate content. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = () => {
    handleGenerate();
  };

  const handleSave = () => {
    // Content is automatically saved when generated
    toast({
      title: "Saved to library",
      description: "Objectives have been saved to your history.",
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
            <Target className="w-8 h-8 text-primary" />
            Learning Objectives Generator
          </h1>
          <p className="text-muted-foreground">
            Generate clear, measurable learning objectives written in simple classroom language.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="animate-slide-up" style={{ animationDelay: "100ms" }}>
            <GeneratorForm
              title="Tell us about your learning goals"
              description="Describe what you want students to learn or be able to do"
              icon={<Target className="w-5 h-5 text-primary" />}
              // NEW CONSOLIDATED DESIGN: Single prompt with user_intent
              userIntent={userIntent}
              onUserIntentChange={setUserIntent}
              numObjectives={numObjectives}
              onNumObjectivesChange={setNumObjectives}
              gradeLevel={gradeLevel}
              onGradeLevelChange={setGradeLevel}
              onSubmit={handleGenerate}
              isLoading={isLoading}
              userIntentPlaceholder="e.g., Understand how bacteria multiply at different temperatures and factors that affect food safety"
            />
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
              // NEW CONSOLIDATED SYSTEM: Enhanced data display
              routingInfo={routingInfo}
              qualityMetrics={qualityMetrics}
              warnings={warnings}
            />
          </div>
        </div>
      </div>
      <GenerationLimitModal open={showLimitModal} onOpenChange={setShowLimitModal} />
    </DashboardLayout>
  );
};

export default LearningObjectives;