import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { GeneratorCard } from "@/components/generators/GeneratorCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BookOpen,
  Target,
  Clock,
  Copy,
  Eye,
  Palette,
  FlaskConical,
  Presentation,
  FileText,
  CheckSquare,
  Mic,
  StickyNote,
  Search,
  Download,
  Heart,
  Calendar,
  CreditCard,
  FileQuestion,
  ClipboardCheck,
  Star,
  Check,
  Loader2,
  BookMarked,
  Image,
  Lightbulb,
  FileCheck,
  Utensils,
  Tag,
  Smile,
  MessageSquare,
  GraduationCap,
  Trash2,
} from "lucide-react";
import { useProfile } from "@/hooks/useProfile";
import { MEMBERSHIP_TIERS } from "@/lib/constants";
import { format, formatDistanceToNow } from "date-fns";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { generatorService, GeneratedContent } from "@/lib/api/generators";
import apiClient from "@/lib/api/client";

interface GenerationItem {
  id: number;
  type: string;
  title: string;
  time: string;
  icon: string;
  category: string;
  content: string;
  contentType: string;
  isFavorite?: boolean;
}

const activeGenerators = [
  {
    title: "Learning Objectives Generator",
    description: "Create clear, measurable learning objectives aligned to your lesson topic and student outcomes.",
    icon: <Target className="w-6 h-6 text-primary" />,
    href: "/objectives",
  },
  {
    title: "Lesson Starter Generator",
    description: "Generate engaging opening prompts or activities that introduce a topic and focus student thinking.",
    icon: <BookOpen className="w-6 h-6 text-primary" />,
    href: "/lesson-starter",
  },
  {
    title: "Discussion Question Generator",
    description: "Generate standalone academic discussion questions usable before, during, or after instruction.",
    icon: <Clock className="w-6 h-6 text-primary" />,
    href: "/check-in",
  },
];

const comingSoonGenerators = [
  // Starter Plan Generators
  {
    title: "Lesson Plan Generator",
    description: "Build structured lesson plans that outline objectives, activities, and assessments in one place.",
    icon: <ClipboardCheck className="w-6 h-6 text-muted-foreground" />,
    href: "/lesson-plan",
  },
  {
    title: "Multiple Choice Quiz Generator",
    description: "Generate ready-to-use multiple choice questions aligned with your lesson content.",
    icon: <FileQuestion className="w-6 h-6 text-muted-foreground" />,
    href: "/quiz",
  },
  {
    title: "Key Terms and Definitions Generator",
    description: "Create student-friendly vocabulary lists with clear definitions for your topic.",
    icon: <BookMarked className="w-6 h-6 text-muted-foreground" />,
    href: "/key-terms",
  },
  // Pro Plan Generators
  {
    title: "Required Reading Generator",
    description: "Generate structured reading content students can review to understand key concepts.",
    icon: <BookOpen className="w-6 h-6 text-muted-foreground" />,
    href: "/required-reading",
  },
  {
    title: "Slide Generator",
    description: "Create slide-ready content with clear headings and key points for presentations.",
    icon: <Presentation className="w-6 h-6 text-muted-foreground" />,
    href: "/slides",
  },
  {
    title: "Worksheet Generator",
    description: "Generate printable worksheets that help students practice and apply concepts.",
    icon: <FileText className="w-6 h-6 text-muted-foreground" />,
    href: "/worksheet",
  },
  {
    title: "Rubric Generator",
    description: "Build clear grading rubrics with defined criteria and performance levels.",
    icon: <CheckSquare className="w-6 h-6 text-muted-foreground" />,
    href: "/rubric",
  },
  {
    title: "Food Science Laboratory Generator",
    description: "Create classroom-appropriate food science lab activities with objectives and procedures.",
    icon: <FlaskConical className="w-6 h-6 text-muted-foreground" />,
    href: "/lab",
  },
  {
    title: "Image Generator",
    description: "Generate educational visuals to support explanations and student understanding.",
    icon: <Image className="w-6 h-6 text-muted-foreground" />,
    href: "/image-generator",
  },
  {
    title: "Project Ideas Generator",
    description: "Generate student project ideas aligned to food science and consumer science topics.",
    icon: <Lightbulb className="w-6 h-6 text-muted-foreground" />,
    href: "/project-ideas",
  },
  {
    title: "Project Proposal Generator",
    description: "Create structured project proposal templates students can use to plan their work.",
    icon: <FileCheck className="w-6 h-6 text-muted-foreground" />,
    href: "/project-proposal",
  },
  {
    title: "Recipe Generator",
    description: "Generate instructional recipes designed for classroom use and concept demonstration.",
    icon: <Utensils className="w-6 h-6 text-muted-foreground" />,
    href: "/recipe",
  },
  {
    title: "Nutrition Label Generator",
    description: "Create Nutrition Facts style labels based on ingredients or recipes for instructional use.",
    icon: <Tag className="w-6 h-6 text-muted-foreground" />,
    href: "/nutrition-label",
  },
  {
    title: "Teacher Jokes Generator",
    description: "Generate light, classroom-appropriate humor related to food science topics.",
    icon: <Smile className="w-6 h-6 text-muted-foreground" />,
    href: "/teacher-jokes",
  },
  {
    title: "Ask Courtney",
    description: "Ask food science questions and receive clear, classroom-ready explanations.",
    icon: <MessageSquare className="w-6 h-6 text-muted-foreground" />,
    href: "/ask-courtney",
  },
];

// Helper function to map content type to icon and category
const getContentTypeInfo = (contentType: string): { icon: string; category: string } => {
  const typeMap: Record<string, { icon: string; category: string }> = {
    lesson_starter: { icon: "📝", category: "Lesson Starter" },
    learning_objectives: { icon: "🎯", category: "Learning Objectives" },
    check_in_question: { icon: "⏰", category: "Discussion Question" },
    
    quiz: { icon: "❓", category: "Quiz" },
  };
  return typeMap[contentType] || { icon: "📄", category: "Other" };
};

// Helper function to safely format dates
const safeFormatDate = (dateString: string | null | undefined, formatStr: string): string | null => {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return null;
    return format(date, formatStr);
  } catch (error) {
    return null;
  }
};


const Index = () => {
  const navigate = useNavigate();
  const { profile, remainingGenerations, isUnlimited, loading: profileLoading } = useProfile();
  const { user } = useAuth();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterDate, setFilterDate] = useState("all");
  const [filterGrade, setFilterGrade] = useState("all");
  const [viewMode, setViewMode] = useState<"recent" | "all" | "favorites">("recent");
  const [selectedItem, setSelectedItem] = useState<GenerationItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
  const [loadingContent, setLoadingContent] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [togglingFavoriteId, setTogglingFavoriteId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<GenerationItem | null>(null);

  const currentTier = profile?.subscription_tier || 'trial';
  const tierKey = currentTier.toUpperCase() as keyof typeof MEMBERSHIP_TIERS;
  const tierInfo = MEMBERSHIP_TIERS[tierKey] || MEMBERSHIP_TIERS.TRIAL; // Fallback to TRIAL if tier not found
  const generationsUsed = profile?.generation_count ?? 0;
  const generationsLimit = profile?.generation_limit === -1 ? null : (profile?.generation_limit ?? 10);
  // Allow access for both 'starter' and 'pro' tiers (anything that's not 'trial')
  const canAccessContentManagement = currentTier === 'starter' || currentTier === 'pro';
  
  // Get display name: use profile display_name, or user's first_name + last_name, or first_name, or email, or "User"
  const displayName = profile?.display_name 
    || (user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : '')
    || user?.first_name 
    || user?.email?.split('@')[0] 
    || 'User';

  // Fetch generated content
  useEffect(() => {
    if (user && canAccessContentManagement) {
      setLoadingContent(true);
      generatorService.listGeneratedContent()
        .then((content) => {
          // Ensure content is always an array
          setGeneratedContent(Array.isArray(content) ? content : []);
        })
        .catch((error) => {
          // On error, set empty array to prevent issues
          setGeneratedContent([]);
          toast({
            title: "Failed to load content",
            description: "Could not fetch your generated content. Please try again.",
            variant: "destructive",
          });
        })
        .finally(() => {
          setLoadingContent(false);
        });
    } else {
      // If user doesn't have access, ensure empty array
      setGeneratedContent([]);
    }
  }, [user, canAccessContentManagement, toast]);

  // Convert GeneratedContent to GenerationItem format
  const contentToItems = (content: GeneratedContent[]): GenerationItem[] => {
    // Ensure content is always an array
    if (!Array.isArray(content)) {
      return [];
    }
    return content.map((item) => {
      const typeInfo = getContentTypeInfo(item.content_type);
      let timeStr = "Recently";
      try {
        const createdDate = new Date(item.created_at);
        if (!isNaN(createdDate.getTime())) {
          timeStr = formatDistanceToNow(createdDate, { addSuffix: true });
        }
      } catch (error) {
        // Use default "Recently" if date parsing fails
      }
      return {
        id: item.id,
        type: item.content_type,
        title: item.title,
        time: timeStr,
        icon: typeInfo.icon,
        category: typeInfo.category,
        content: item.content,
        contentType: item.content_type,
        isFavorite: item.is_favorite || false,
      };
    });
  };

  // Ensure generatedContent is always an array
  const allItems = contentToItems(Array.isArray(generatedContent) ? generatedContent : []);
  const recentGenerations = allItems.slice(0, 10);
  // Filter favorites - ensure we check both isFavorite (from GenerationItem) and is_favorite (from API)
  const favoriteGenerations = allItems.filter(item => {
    // Check isFavorite property (from GenerationItem conversion)
    if (item.isFavorite === true) return true;
    // Also check if the original content has is_favorite set
    const originalContent = generatedContent.find(c => c.id === item.id);
    return originalContent?.is_favorite === true;
  });

  const handleCopy = (item: GenerationItem) => {
    navigator.clipboard.writeText(item.content);
    setCopiedId(item.title);
    toast({
      title: "Copied to clipboard",
      description: `"${item.title}" has been copied.`,
    });
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleView = (item: GenerationItem) => {
    setSelectedItem(item);
  };

  const handleDownload = async (item: GenerationItem, format: 'docx' | 'pdf') => {
    if (!item.id) return;
    
    setDownloadingId(item.id);
    try {
      const response = await apiClient.get(
        `/generators/${item.id}/export/${format}/`,
        { responseType: 'blob' }
      );
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${item.title}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Download started",
        description: `Your ${format.toUpperCase()} file is downloading.`,
      });
    } catch (error: any) {
      toast({
        title: "Download failed",
        description: error?.response?.data?.error || `Failed to download ${format.toUpperCase()} file. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setDownloadingId(null);
    }
  };

  const handleToggleFavorite = async (item: GenerationItem) => {
    if (!item.id) return;
    
    setTogglingFavoriteId(item.id);
    try {
      const result = await generatorService.toggleFavorite(item.id);
      
      // Update the item in generatedContent immediately for instant feedback
      setGeneratedContent(prevContent => 
        prevContent.map(content => 
          content.id === item.id 
            ? { ...content, is_favorite: result.is_favorite }
            : content
        )
      );
      
      // Refetch content to ensure it's in sync with the server
      // This ensures the favorites tab shows the updated content
      if (user && canAccessContentManagement) {
        try {
          const updatedContent = await generatorService.listGeneratedContent();
          setGeneratedContent(Array.isArray(updatedContent) ? updatedContent : []);
        } catch (fetchError) {
          // If refetch fails, the local update should still work
          console.warn('Failed to refetch content after favorite toggle:', fetchError);
        }
      }
      
      toast({
        title: result.is_favorite ? "Added to favorites" : "Removed from favorites",
        description: result.message,
      });
    } catch (error: any) {
      toast({
        title: "Failed to update favorite",
        description: error?.response?.data?.error || "Could not update favorite status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setTogglingFavoriteId(null);
    }
  };

  const handleDeleteClick = (item: GenerationItem) => {
    setItemToDelete(item);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete || !itemToDelete.id) return;
    
    setDeletingId(itemToDelete.id);
    try {
      await generatorService.deleteContent(itemToDelete.id);
      
      // Remove the item from the local state
      setGeneratedContent(prevContent => 
        prevContent.filter(content => content.id !== itemToDelete.id)
      );
      
      // Refetch content to ensure it's in sync with the server
      if (user && canAccessContentManagement) {
        try {
          const updatedContent = await generatorService.listGeneratedContent();
          setGeneratedContent(Array.isArray(updatedContent) ? updatedContent : []);
        } catch (fetchError) {
          console.warn('Failed to refetch content after delete:', fetchError);
        }
      }
      
      toast({
        title: "Content deleted",
        description: `"${itemToDelete.title}" has been deleted successfully.`,
      });
    } catch (error: any) {
      toast({
        title: "Failed to delete content",
        description: error?.response?.data?.error || "Could not delete content. Please try again.",
        variant: "destructive",
      });
    } finally {
      setDeletingId(null);
      setDeleteConfirmOpen(false);
      setItemToDelete(null);
    }
  };

  // Show loading state while profile is loading
  if (profileLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <>
      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Content</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{itemToDelete?.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deletingId !== null}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={deletingId !== null}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deletingId !== null ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* View Content Dialog */}
      <Dialog open={!!selectedItem} onOpenChange={() => setSelectedItem(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <span className="text-2xl">{selectedItem?.icon}</span>
              {selectedItem?.title}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="secondary">{selectedItem?.category}</Badge>
              <span>•</span>
              <span>{selectedItem?.time}</span>
            </div>
            <div className="bg-muted/50 rounded-lg p-4 whitespace-pre-wrap text-sm">
              {selectedItem?.content}
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => selectedItem && handleCopy(selectedItem)}
              >
                <Copy className="w-4 h-4 mr-2" />
                Copy Content
              </Button>
              <Button 
                variant="outline"
                onClick={() => selectedItem && handleDownload(selectedItem, 'docx')}
                title="Download DOCX"
              >
                <Download className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome Section with Plan Info */}
        <div className="animate-fade-in">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
                Welcome back, {displayName}!
              </h1>
              <p className="text-muted-foreground">
                {isUnlimited ? (
                  <span>You have <span className="font-semibold text-foreground">unlimited</span> generations</span>
                ) : (
                  <>
                    You have{" "}
                    <span className="font-semibold text-foreground">
                      {remainingGenerations >= 0 ? remainingGenerations : 0}
                    </span>{" "}
                    generations remaining this month
                  </>
                )}
              </p>
            </div>

            {/* Plan Card */}
            <Card className="lg:min-w-[300px]">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <CreditCard className="w-5 h-5 text-primary" />
                    <span className="font-semibold">{tierInfo?.name || 'Trial'} Plan</span>
                  </div>
                  <Badge variant="secondary">Active</Badge>
                </div>
                <div className="space-y-2 text-sm">
                  {safeFormatDate(profile?.subscription_end_date || null, 'MMMM d, yyyy') && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="w-4 h-4" />
                      <span>
                        {currentTier === 'trial' 
                          ? `Ends: ${safeFormatDate(profile?.subscription_end_date || null, 'MMMM d, yyyy')}`
                          : profile?.billing_interval 
                            ? `Renews ${profile.billing_interval === 'year' ? 'yearly' : 'monthly'}: ${safeFormatDate(profile?.subscription_end_date || null, 'MMMM d, yyyy')}`
                            : `Renews monthly: ${safeFormatDate(profile?.subscription_end_date || null, 'MMMM d, yyyy')}`
                        }
                      </span>
                    </div>
                  )}
                  {!isUnlimited && generationsLimit !== null && (
                    <>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{
                            width: `${Math.min((generationsUsed / generationsLimit) * 100, 100)}%`,
                          }}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {generationsUsed}/{generationsLimit} generations used
                      </p>
                    </>
                  )}
                  {isUnlimited && (
                    <p className="text-xs text-muted-foreground">
                      {generationsUsed} generations used (Unlimited)
                    </p>
                  )}
                  {!isUnlimited && generationsLimit === null && (
                    <p className="text-xs text-muted-foreground">
                      {generationsUsed} generations used
                    </p>
                  )}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-3"
                  onClick={() => navigate('/pricing')}
                >
                  Upgrade Plan
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Active Generators */}
        <section className="animate-slide-up" style={{ animationDelay: "100ms" }}>
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-xl font-semibold">Available Generators</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {(Array.isArray(activeGenerators) ? activeGenerators : []).map((generator) => (
              <GeneratorCard key={generator.title} {...generator} />
            ))}
          </div>
        </section>

        {/* Coming Soon Generators */}
        <section className="animate-slide-up" style={{ animationDelay: "150ms" }}>
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-xl font-semibold">Coming Soon</h2>
            <span className="text-xs bg-accent/10 text-accent px-2 py-1 rounded-full font-medium">
              Future Modules
            </span>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {(Array.isArray(comingSoonGenerators) ? comingSoonGenerators : []).map((generator) => (
              <GeneratorCard key={generator.title} {...generator} comingSoon />
            ))}
          </div>
        </section>

        {/* Generation Management Section */}
        <section className="animate-slide-up" style={{ animationDelay: "200ms" }}>
          <Card className={`overflow-visible ${!canAccessContentManagement ? 'opacity-50 pointer-events-none' : ''}`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Content Management
                {!canAccessContentManagement && (
                  <Badge variant="secondary" className="ml-2">Starter & Pro Only</Badge>
                )}
              </CardTitle>
            </CardHeader>
            {!canAccessContentManagement ? (
              <CardContent className="space-y-4">
                <div className="text-center py-8 text-muted-foreground">
                  <p className="mb-2">Content Management is available for Starter and Pro plans.</p>
                  <Button onClick={() => navigate('/pricing')} className="mt-4">
                    Upgrade to Access
                  </Button>
                </div>
              </CardContent>
            ) : (
            <CardContent className="space-y-6 overflow-visible relative">
              {/* Search and Filters */}
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search your generations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex gap-2 flex-wrap relative z-10">
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Tool Type" />
                    </SelectTrigger>
                    <SelectContent className="z-[9999]" position="popper">
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="lesson-starter">Lesson Starter</SelectItem>
                      <SelectItem value="objectives">Learning Objectives</SelectItem>
                      
                      <SelectItem value="worksheet">Worksheet</SelectItem>
                      <SelectItem value="rubric">Rubric</SelectItem>
                      <SelectItem value="activity">Classroom Activity</SelectItem>
                      <SelectItem value="lesson-notes">Lesson Notes</SelectItem>
                      <SelectItem value="slides">Slides</SelectItem>
                      <SelectItem value="lesson-plan">Lesson Plan</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterDate} onValueChange={setFilterDate}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Date" />
                    </SelectTrigger>
                    <SelectContent className="z-[9999]" position="popper">
                      <SelectItem value="all">All Time</SelectItem>
                      <SelectItem value="today">Today</SelectItem>
                      <SelectItem value="week">This Week</SelectItem>
                      <SelectItem value="month">This Month</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filterGrade} onValueChange={setFilterGrade}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Grade Level" />
                    </SelectTrigger>
                    <SelectContent className="z-[9999]" position="popper">
                      <SelectItem value="all">All Grades</SelectItem>
                      <SelectItem value="elementary">Elementary</SelectItem>
                      <SelectItem value="middle">Middle School</SelectItem>
                      <SelectItem value="high">High School</SelectItem>
                      <SelectItem value="college">College</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Download All
                </Button>
              </div>

              {/* View Mode Tabs */}
              <div className="flex gap-2 border-b">
                <Button
                  variant={viewMode === "recent" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("recent")}
                  className="rounded-b-none"
                >
                  Recent Generations
                </Button>
                <Button
                  variant={viewMode === "all" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("all")}
                  className="rounded-b-none"
                >
                  All Generations
                </Button>
                <Button
                  variant={viewMode === "favorites" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("favorites")}
                  className="rounded-b-none"
                >
                  Favorites
                </Button>
              </div>

              {/* Content Display based on view mode */}
              {loadingContent ? (
                <div className="text-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Loading your content...</p>
                </div>
              ) : recentGenerations.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No generated content yet. Start creating content using the generators above!</p>
                </div>
              ) : (
              <>
              {viewMode === "recent" && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Recent Generations</h3>
                  </div>
                  <div className="space-y-3">
                    {(Array.isArray(recentGenerations) ? recentGenerations.slice(0, 10) : []).map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{item.icon}</span>
                          <div>
                            <h4 className="font-medium text-foreground">{item.title}</h4>
                            <p className="text-sm text-muted-foreground">
                              {item.category} • {item.time}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title={item.isFavorite ? "Remove from favorites" : "Add to favorites"}
                            onClick={() => handleToggleFavorite(item)}
                            disabled={togglingFavoriteId === item.id}
                          >
                            {togglingFavoriteId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Heart className={`w-4 h-4 ${item.isFavorite ? 'fill-destructive text-destructive' : ''}`} />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="View"
                            onClick={() => handleView(item)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Copy"
                            onClick={() => handleCopy(item)}
                          >
                            {copiedId === item.title ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Download DOCX"
                            onClick={() => handleDownload(item, 'docx')}
                            disabled={downloadingId === item.id}
                          >
                            {downloadingId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Download className="w-4 h-4" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Delete"
                            onClick={() => handleDeleteClick(item)}
                            disabled={deletingId === item.id}
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                          >
                            {deletingId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {viewMode === "all" && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">All Generations</h3>
                    <p className="text-sm text-muted-foreground">
                      {allItems.length} total items
                    </p>
                  </div>
                  <div className="space-y-3">
                    {(Array.isArray(allItems) ? allItems : []).map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{item.icon}</span>
                          <div>
                            <h4 className="font-medium text-foreground">{item.title}</h4>
                            <p className="text-sm text-muted-foreground">
                              {item.category} • {item.time || "Previously saved"}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title={item.isFavorite ? "Remove from favorites" : "Add to favorites"}
                            onClick={() => handleToggleFavorite(item)}
                            disabled={togglingFavoriteId === item.id}
                          >
                            {togglingFavoriteId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Heart className={`w-4 h-4 ${item.isFavorite ? 'fill-destructive text-destructive' : ''}`} />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="View"
                            onClick={() => handleView({ ...item, type: 'all', time: item.time || 'Previously saved' } as GenerationItem)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Copy"
                            onClick={() => handleCopy({ ...item, type: 'all', time: item.time || 'Previously saved' } as GenerationItem)}
                          >
                            {copiedId === item.title ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Download DOCX"
                            onClick={() => handleDownload(item, 'docx')}
                            disabled={downloadingId === item.id}
                          >
                            {downloadingId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Download className="w-4 h-4" />
                            )}
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            title="Delete"
                            onClick={() => handleDeleteClick({ ...item, type: 'all', time: item.time || 'Previously saved' } as GenerationItem)}
                            disabled={deletingId === item.id}
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                          >
                            {deletingId === item.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {viewMode === "favorites" && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Heart className="w-4 h-4 text-destructive fill-destructive" />
                      Favorites
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {favoriteGenerations.length} {favoriteGenerations.length === 1 ? 'item' : 'items'}
                    </p>
                  </div>
                  {favoriteGenerations.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Heart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No favorites yet. Click the heart icon on any content to add it to your favorites.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {(Array.isArray(favoriteGenerations) ? favoriteGenerations : []).map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">{item.icon}</span>
                            <div>
                              <h4 className="font-medium text-foreground">{item.title}</h4>
                              <p className="text-sm text-muted-foreground">
                                {item.category} • {item.time || "Previously saved"}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              title="Remove from favorites"
                              onClick={() => handleToggleFavorite(item)}
                              disabled={togglingFavoriteId === item.id}
                            >
                              {togglingFavoriteId === item.id ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Heart className="w-4 h-4 fill-destructive text-destructive" />
                              )}
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              title="View"
                              onClick={() => handleView({ ...item, type: 'favorites', time: item.time || 'Previously saved' } as GenerationItem)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              title="Copy"
                              onClick={() => handleCopy({ ...item, type: 'favorites', time: item.time || 'Previously saved' } as GenerationItem)}
                            >
                              {copiedId === item.title ? (
                                <Check className="w-4 h-4 text-green-500" />
                              ) : (
                                <Copy className="w-4 h-4" />
                              )}
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              title="Download DOCX"
                              onClick={() => handleDownload(item, 'docx')}
                              disabled={downloadingId === item.id}
                            >
                              {downloadingId === item.id ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Download className="w-4 h-4" />
                              )}
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              title="Delete"
                              onClick={() => handleDeleteClick({ ...item, type: 'favorites', time: item.time || 'Previously saved' } as GenerationItem)}
                              disabled={deletingId === item.id}
                              className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            >
                              {deletingId === item.id ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Trash2 className="w-4 h-4" />
                              )}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              </>
              )}
            </CardContent>
            )}
          </Card>
        </section>
      </div>
    </DashboardLayout>
    </>
  );
};

export default Index;