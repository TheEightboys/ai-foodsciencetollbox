import { useState } from "react";
import type React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy, Check, RefreshCw, Save, Sparkles, Download, Heart, Info, TrendingUp, AlertTriangle } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface OutputSection {
  title: string;
  icon: string;
  content: string;
}

interface OutputDisplayProps {
  sections: OutputSection[];
  isLoading?: boolean;
  onRegenerate?: () => void;
  onSave?: () => void;
  onFavorite?: () => void;
  isFavorited?: boolean;
  contentId?: number; // ID of the generated content for downloads
  docxUrl?: string; // URL for DOCX download
  pdfUrl?: string; // URL for PDF download (deprecated - kept for backward compatibility)
  
  // NEW CONSOLIDATED SYSTEM: Enhanced response data
  routingInfo?: {
    domain: string;
    confidence: number;
    apply_food_overlay: boolean;
    domain_description: string;
    fallback_used?: boolean;
  };
  qualityMetrics?: {
    objectives_generated: number;
    target_objectives: number;
    grade_level_match: boolean;
    domain_confidence: number;
    has_food_overlay: boolean;
    fallback_used?: boolean;
  };
  warnings?: string[];
}

export function OutputDisplay({
  sections,
  isLoading = false,
  onRegenerate,
  onSave,
  onFavorite,
  isFavorited = false,
  contentId,
  docxUrl,
  pdfUrl,
  // NEW CONSOLIDATED SYSTEM: Enhanced response data
  routingInfo,
  qualityMetrics,
  warnings,
}: OutputDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const text = sections.map((s) => `${s.title}\n${s.content}`).join("\n\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast({
      title: "Copied to clipboard",
      description: "Content has been copied successfully.",
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = async (format: "docx" | "pdf") => {
    const selectedUrl = format === "docx" ? docxUrl : pdfUrl;
    if (!selectedUrl && !contentId) {
      toast({
        title: "Download unavailable",
        description: "Document URL not available. Please regenerate the content.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Get the API base URL
      let apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 
        (typeof window !== 'undefined' ? window.location.origin : '');
      
      // Ensure apiBaseUrl ends with /api
      if (!apiBaseUrl.endsWith('/api')) {
        apiBaseUrl = apiBaseUrl.replace(/\/api\/?$/, '') + '/api';
      }
      
      // Construct the download URL (ensure it's absolute)
      let downloadUrl = selectedUrl;
      
      // If no docxUrl provided, construct from contentId
      if (!downloadUrl && contentId) {
        downloadUrl = `${apiBaseUrl}/generators/${contentId}/export/${format}/`;
      }
      
      // If URL is relative, make it absolute
      if (downloadUrl && downloadUrl.startsWith('/')) {
        downloadUrl = `${apiBaseUrl}${downloadUrl}`;
      }
      
      // Force HTTPS if current page is HTTPS (prevent mixed content)
      if (typeof window !== 'undefined' && window.location.protocol === 'https:' && downloadUrl.startsWith('http://')) {
        downloadUrl = downloadUrl.replace('http://', 'https://');
      }
      
      // If URL contains api.foodsciencetoolbox.com, ensure it's HTTPS
      if (downloadUrl.includes('api.foodsciencetoolbox.com') && downloadUrl.startsWith('http://')) {
        downloadUrl = downloadUrl.replace('http://', 'https://');
      }
      
      // Fetch the file with credentials to include auth token
      const accessToken = localStorage.getItem('access_token');
      const response = await fetch(downloadUrl, {
        method: 'GET',
        credentials: 'include',
        headers: accessToken ? {
          'Authorization': `Bearer ${accessToken}`,
        } : {},
      });
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = format === "docx" ? "document.docx" : "document.pdf";
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // Get blob and create download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Download started",
        description: `Your ${format.toUpperCase()} file is downloading.`,
      });
    } catch (error) {
      toast({
        title: "Download failed",
        description: "Failed to download document. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDownloadWord = async () => {
    await handleDownload("docx");
  };

  const handleDownloadPdf = async () => {
    await handleDownload("pdf");
  };


  if (isLoading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary animate-spin" />
            Generating...
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <div className="h-4 bg-muted rounded w-24" />
              <div className="h-20 bg-muted rounded" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (sections.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="font-serif font-semibold text-lg mb-2">
            Your content will appear here
          </h3>
          <p className="text-sm text-muted-foreground max-w-sm mx-auto">
            Fill in the form above and click generate to create AI-powered
            content for your classroom.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="space-y-1">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            Generated Content
          </CardTitle>
          <p className="text-sm text-muted-foreground italic">
            Preview
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Immediate Download Buttons */}
          <Button variant="outline" size="sm" onClick={handleDownloadWord} title="Download as Word">
            <Download className="w-4 h-4 mr-1" />
            Word
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownloadPdf} title="Download as PDF">
            <Download className="w-4 h-4 mr-1" />
            PDF
          </Button>

          {onFavorite && (
            <Button 
              variant={isFavorited ? "default" : "outline"} 
              size="sm" 
              onClick={onFavorite}
            >
              <Heart className={`w-4 h-4 mr-1 ${isFavorited ? "fill-current" : ""}`} />
              {isFavorited ? "Favorited" : "Favorite"}
            </Button>
          )}

          {onRegenerate && (
            <Button variant="outline" size="sm" onClick={onRegenerate}>
              <RefreshCw className="w-4 h-4 mr-1" />
              Regenerate
            </Button>
          )}

          {onSave && (
            <Button variant="default" size="sm" onClick={onSave}>
              <Save className="w-4 h-4 mr-1" />
              Save
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* NEW CONSOLIDATED SYSTEM: Quality Metrics and Routing Info */}
        {(routingInfo || qualityMetrics || warnings) && (
          <div className="space-y-4 mb-6">
            {/* Routing Information */}
            {routingInfo && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-blue-600" />
                  <h4 className="font-semibold text-blue-900">Domain Analysis</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="font-medium text-blue-700">Domain:</span>
                    <span className="ml-2 text-blue-900 capitalize">{routingInfo.domain}</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-700">Confidence:</span>
                    <span className="ml-2 text-blue-900">{Math.round(routingInfo.confidence * 100)}%</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-700">Description:</span>
                    <span className="ml-2 text-blue-900">{routingInfo.domain_description}</span>
                  </div>
                  {routingInfo.apply_food_overlay && (
                    <div>
                      <span className="font-medium text-blue-700">Food Science:</span>
                      <span className="ml-2 text-blue-900">Applied</span>
                    </div>
                  )}
                  {routingInfo.fallback_used && (
                    <div className="flex items-center">
                      <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                      <span className="text-yellow-800">Fallback system used</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quality Metrics */}
            {qualityMetrics && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <h4 className="font-semibold text-green-900">Quality Metrics</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <span className="font-medium text-green-700">Objectives:</span>
                    <span className="ml-2 text-green-900">{qualityMetrics.objectives_generated}/{qualityMetrics.target_objectives}</span>
                  </div>
                  <div>
                    <span className="font-medium text-green-700">Grade Match:</span>
                    <span className={`ml-2 ${qualityMetrics.grade_level_match ? 'text-green-900' : 'text-yellow-900'}`}>
                      {qualityMetrics.grade_level_match ? '✓ Match' : '⚠ Review'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-green-700">Domain Score:</span>
                    <span className="ml-2 text-green-900">{Math.round(qualityMetrics.domain_confidence * 100)}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Warnings */}
            {warnings && warnings.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  <h4 className="font-semibold text-yellow-900">Warnings</h4>
                </div>
                <div className="space-y-2 text-sm">
                  {warnings.map((warning, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <span className="text-yellow-800">•</span>
                      <span className="text-yellow-900">{warning}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {sections.map((section, index) => {
          // Process content to number Success Criteria items
          const lines = section.content.split('\n');
          const processedLines: React.ReactNode[] = [];
          let inSuccessCriteria = false;
          let successCriteriaCounter = 1;
          let inLearningObjectives = false;
          let learningObjectivesCounter = 1;
          
          for (let idx = 0; idx < lines.length; idx++) {
            let line = lines[idx];
            let lineTrimmed = line.trim();
            const lineLower = lineTrimmed.toLowerCase();
            
            // Remove "(Section header: ...)" text that might still be present
            if (lineLower.includes('(section header')) {
              // Remove the entire line if it's just the section header instruction
              if (/^\s*\(section header[^)]*\)\s*$/i.test(lineTrimmed)) {
                continue; // Skip this line
              }
              // Otherwise, remove just the "(Section header: ...)" part from the line
              line = line.replace(/\(section header[^)]*\)/gi, '').trim();
              lineTrimmed = line.trim();
              if (!lineTrimmed) {
                continue; // Skip if line is now empty
              }
            }
            
            // Format lines with Grade Level, Time Needed, Topic (bold labels)
            if (lineTrimmed.startsWith('Grade Level:') || lineTrimmed.startsWith('Topic:') || lineTrimmed.startsWith('Time Needed:')) {
              // Split label and value
              const colonIndex = lineTrimmed.indexOf(':');
              if (colonIndex > 0) {
                const label = lineTrimmed.substring(0, colonIndex + 1);
                const value = lineTrimmed.substring(colonIndex + 1).trim();
                processedLines.push(
                  <div key={idx} className="mb-1">
                    <span className="font-bold">{label}</span> {value}
                  </div>
                );
              } else {
                processedLines.push(
                  <div key={idx} className="mb-1">
                    {line}
                  </div>
                );
              }
              continue;
            }
            
            // Also handle old format with **bold** markers (for backward compatibility)
            if (line.includes('**Grade Level:**') || line.includes('**Topic:**') || line.includes('**Time Needed:**')) {
              const parts = line.split(/(\*\*.*?\*\*)/g);
              processedLines.push(
                <div key={idx} className="mb-1">
                  {parts.map((part, partIdx) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                      return (
                        <span key={partIdx} className="font-bold">
                          {part.replace(/\*\*/g, '')}
                        </span>
                      );
                    }
                    return <span key={partIdx}>{part}</span>;
                  })}
                </div>
              );
              continue;
            }
            
            // Check if line is a subheading (common section headers)
            const isSubheading = lineTrimmed && (
              lineTrimmed === 'Learning Objectives' ||
              lineTrimmed === 'Success Criteria' ||
              lineTrimmed === 'Hook' ||
              lineTrimmed === 'Why This Lesson Matters' ||
              lineTrimmed === 'Background Connection' ||
              lineTrimmed === 'Key Ideas to Explore' ||
              lineTrimmed === 'Introductory Teacher Script' ||
              lineTrimmed === 'Purpose' ||
              lineTrimmed === 'Prompt' ||
              lineTrimmed.startsWith('Learning Objectives') ||
              lineTrimmed.startsWith('Success Criteria') ||
              lineTrimmed.startsWith('Hook') ||
              lineTrimmed.startsWith('Why This Lesson Matters') ||
              lineTrimmed.startsWith('Background Connection') ||
              lineTrimmed.startsWith('Key Ideas to Explore') ||
              lineTrimmed.startsWith('Introductory Teacher Script') ||
              lineTrimmed.startsWith('Purpose') ||
              lineTrimmed.startsWith('Prompt')
            ) && lineTrimmed.length < 50; // Short lines are likely headers
            
            if (isSubheading) {
              // Track which section we're in
              if (lineTrimmed === 'Learning Objectives' || lineTrimmed.startsWith('Learning Objectives')) {
                inLearningObjectives = true;
                inSuccessCriteria = false;
                learningObjectivesCounter = 1;
              } else if (lineTrimmed === 'Success Criteria' || lineTrimmed.startsWith('Success Criteria')) {
                inSuccessCriteria = true;
                inLearningObjectives = false;
                successCriteriaCounter = 1;
              } else {
                inLearningObjectives = false;
                inSuccessCriteria = false;
              }
              
              processedLines.push(
                <div key={idx} className="mb-2 mt-4">
                  <strong className="font-bold text-foreground">{lineTrimmed}</strong>
                </div>
              );
              continue;
            }
            
            // Skip intro lines that should not be numbered
            // Check if this is an intro line (even if it has a number prefix)
            let isIntroLine = false;
            let introContent = lineTrimmed;
            
            if (inLearningObjectives) {
              const lowerLine = lineTrimmed.toLowerCase();
              if (lowerLine.includes('by the end of this lesson') || lowerLine.includes('students will be able to')) {
                isIntroLine = true;
                // Remove number prefix if present (e.g., "1. By the end..." -> "By the end...")
                introContent = lineTrimmed.replace(/^\d+\.\s*/, '').trim();
              }
            } else if (inSuccessCriteria) {
              const lowerLine = lineTrimmed.toLowerCase();
              if (lowerLine.includes('students will demonstrate success') || lowerLine.includes('when they can')) {
                isIntroLine = true;
                // Remove number prefix if present
                introContent = lineTrimmed.replace(/^\d+\.\s*/, '').trim();
              }
            }
            
            if (isIntroLine) {
              // Display intro line without numbering
              processedLines.push(
                <div key={idx} className="mb-2">{introContent}</div>
              );
              continue;
            }
            
            // Check for non-objective conversational/closing text in Learning Objectives
            if (inLearningObjectives) {
              const lowerLine = lineTrimmed.toLowerCase();
              // Patterns that indicate non-objective closing text
              const nonObjectivePatterns = [
                /^(these objectives|these goals|these learning objectives|remember|note that|keep in mind|as you|when you|you can|you will|this lesson|the lesson|today|we will|we'll|let's|it's important|in conclusion|to summarize|finally)/,
                /^(students should|teachers should|educators should)/,
                /^by (completing|finishing|the end of)/,
              ];
              
              // Check if this line is conversational/closing text (not an objective)
              let isNonObjective = false;
              for (const pattern of nonObjectivePatterns) {
                if (pattern.test(lowerLine)) {
                  isNonObjective = true;
                  break;
                }
              }
              
              // Also check for conversational phrases
              const conversationalPhrases = [
                'remember that', 'note that', 'keep in mind', 'as you', 'when you',
                'this lesson will', 'today we will', 'we\'ll', 'let\'s', 'it\'s important',
                'in conclusion', 'to summarize', 'finally', 'these objectives help',
                'these goals', 'by completing', 'by finishing'
              ];
              
              for (const phrase of conversationalPhrases) {
                if (lowerLine.includes(phrase) && !/^\d+[\.\)]?\s*/.test(lineTrimmed)) {
                  isNonObjective = true;
                  break;
                }
              }
              
              // If it's non-objective text, stop processing Learning Objectives
              if (isNonObjective) {
                inLearningObjectives = false;
                continue; // Skip this line
              }
            }
            
            // Check if this is a bullet point or numbered item in Success Criteria or Learning Objectives
            if (inSuccessCriteria && (lineTrimmed.startsWith('•') || lineTrimmed.startsWith('-') || lineTrimmed.startsWith('*'))) {
              // Convert bullet to number for Success Criteria
              const content = lineTrimmed.replace(/^[•\-\*]\s*/, '').trim();
              if (content) {
                processedLines.push(
                  <div key={idx} className="mb-1 ml-4">
                    {successCriteriaCounter}. {content}
                  </div>
                );
                successCriteriaCounter++;
                continue;
              }
            } else if (inLearningObjectives && (lineTrimmed.startsWith('•') || lineTrimmed.startsWith('-') || lineTrimmed.startsWith('*') || /^\d+\./.test(lineTrimmed))) {
              // Convert bullet to number for Learning Objectives, or use existing number
              let content = lineTrimmed;
              let number = learningObjectivesCounter;
              
              // If already numbered, extract the number and content
              const numberedMatch = lineTrimmed.match(/^(\d+)\.\s*(.+)$/);
              if (numberedMatch) {
                number = parseInt(numberedMatch[1]);
                content = numberedMatch[2].trim();
              } else {
                // Remove bullet and use counter
                content = lineTrimmed.replace(/^[•\-\*]\s*/, '').trim();
              }
              
              // Verify this looks like an objective (starts with action verb)
              const actionVerbs = ['identify', 'list', 'describe', 'explain', 'demonstrate', 'analyze', 
                                 'compare', 'apply', 'evaluate', 'justify', 'assess', 'propose', 'synthesize',
                                 'name', 'show', 'tell', 'create', 'develop', 'design'];
              const contentLower = content.toLowerCase();
              const startsWithVerb = actionVerbs.some(verb => contentLower.startsWith(verb + ' '));
              
              if (content && startsWithVerb) {
                processedLines.push(
                  <div key={idx} className="mb-1 ml-4">
                    {number}. {content}
                  </div>
                );
                learningObjectivesCounter = number + 1; // Update counter
                continue;
              } else if (content && !startsWithVerb) {
                // Doesn't look like an objective - might be closing text
                inLearningObjectives = false;
                continue;
              }
            }
            
            // Also handle Success Criteria items that might already be numbered
            if (inSuccessCriteria && /^\d+\./.test(lineTrimmed)) {
              // Extract number and content, renumber starting from counter
              const numberedMatch = lineTrimmed.match(/^(\d+)\.\s*(.+)$/);
              if (numberedMatch) {
                const content = numberedMatch[2].trim();
                processedLines.push(
                  <div key={idx} className="mb-1 ml-4">
                    {successCriteriaCounter}. {content}
                  </div>
                );
                successCriteriaCounter++;
                continue;
              }
            } else if (inSuccessCriteria || inLearningObjectives) {
              // Check if line already starts with a number (already numbered)
              if (/^\d+\.\s+/.test(lineTrimmed)) {
                const numberedMatch = lineTrimmed.match(/^(\d+)\.\s*(.+)$/);
                if (numberedMatch) {
                  const content = numberedMatch[2].trim();
                  
                  // For Learning Objectives, verify it looks like an objective
                  if (inLearningObjectives) {
                    const actionVerbs = ['identify', 'list', 'describe', 'explain', 'demonstrate', 'analyze', 
                                         'compare', 'apply', 'evaluate', 'justify', 'assess', 'propose', 'synthesize',
                                         'name', 'show', 'tell', 'create', 'develop', 'design'];
                    const contentLower = content.toLowerCase();
                    const startsWithVerb = actionVerbs.some(verb => contentLower.startsWith(verb + ' '));
                    
                    if (!startsWithVerb) {
                      // Doesn't look like an objective - stop processing
                      inLearningObjectives = false;
                      continue;
                    }
                  }
                  
                  const currentCounter = inSuccessCriteria ? successCriteriaCounter : learningObjectivesCounter;
                  processedLines.push(
                    <div key={idx} className="mb-1 ml-4">
                      {currentCounter}. {content}
                    </div>
                  );
                  if (inSuccessCriteria) {
                    successCriteriaCounter++;
                  } else {
                    learningObjectivesCounter++;
                  }
                  continue;
                }
              }
            }
            
            // Regular line
            processedLines.push(
              <div key={idx}>{line || '\u00A0'}</div>
            );
          }
          
          return (
            <div
              key={index}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">{section.icon}</span>
                <h4 className="font-semibold text-foreground">{section.title}</h4>
              </div>
              <div className="bg-muted/50 rounded-lg p-4 text-foreground/90 leading-relaxed whitespace-pre-wrap">
                {processedLines}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}