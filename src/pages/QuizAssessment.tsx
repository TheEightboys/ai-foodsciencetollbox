import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { OutputDisplay } from "@/components/generators/OutputDisplay";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { ArrowLeft, FileQuestion, Sparkles, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

import { GRADE_LEVELS, TOPIC_CATEGORIES, ASSESSMENT_TYPES } from "@/lib/constants";

const gradeLevels = GRADE_LEVELS;
const topicCategories = TOPIC_CATEGORIES;
const assessmentTypes = ASSESSMENT_TYPES;

const QuizAssessment = () => {
  const [topicCategory, setTopicCategory] = useState("");
  const [topic, setTopic] = useState("");
  const [gradeLevel, setGradeLevel] = useState("high");
  const [assessmentType, setAssessmentType] = useState("multiple-choice");
  const [questionCount, setQuestionCount] = useState([10]);
  const [additionalDetails, setAdditionalDetails] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [output, setOutput] = useState<{ title: string; icon: string; content: string }[]>([]);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast({
        title: "Topic required",
        description: "Please enter a topic to generate an assessment.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setOutput([]);

    // Simulate AI generation
    setTimeout(() => {
      const questions = Array.from({ length: questionCount[0] }, (_, i) => {
        if (assessmentType === "multiple-choice" || assessmentType === "mixed") {
          return `${i + 1}. What is the primary effect of ${topic.toLowerCase()} in food preparation?\n   A) Option A\n   B) Option B\n   C) Option C\n   D) Option D`;
        } else if (assessmentType === "true-false") {
          return `${i + 1}. ${topic} is commonly used in food preservation. (True/False)`;
        } else if (assessmentType === "fill-blank") {
          return `${i + 1}. The process of ${topic.toLowerCase()} involves __________ to achieve the desired result.`;
        } else {
          return `${i + 1}. Explain how ${topic.toLowerCase()} affects food quality and safety.`;
        }
      }).join("\n\n");

      setOutput([
        {
          title: "ASSESSMENT QUESTIONS",
          icon: "📝",
          content: questions,
        },
        {
          title: "ANSWER KEY",
          icon: "✅",
          content: `Answer key for the ${questionCount[0]} ${assessmentType} questions on ${topic}.\n\n(Answers would be generated here based on the questions above)`,
        },
        {
          title: "ASSESSMENT INFO",
          icon: "📊",
          content: `Topic: ${topic}\nGrade Level: ${gradeLevel.charAt(0).toUpperCase() + gradeLevel.slice(1)} School\nType: ${assessmentTypes.find(t => t.value === assessmentType)?.label}\nTotal Questions: ${questionCount[0]}`,
        },
      ]);
      setIsLoading(false);
      toast({
        title: "Assessment generated!",
        description: `${questionCount[0]} questions are ready to use.`,
      });
    }, 2000);
  };

  const handleRegenerate = () => {
    handleGenerate();
  };

  const handleSave = () => {
    toast({
      title: "Saved to library",
      description: "Assessment has been saved to your history.",
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/">
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to Dashboard
            </Link>
          </Button>
        </div>

        <div className="animate-fade-in">
          <h1 className="font-serif text-2xl md:text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <FileQuestion className="w-8 h-8 text-primary" />
            Quiz & Assessment Generator
          </h1>
          <p className="text-muted-foreground">
            Create quizzes and assessments with various question types for your food science lessons.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="animate-slide-up" style={{ animationDelay: "100ms" }}>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center">
                    <FileQuestion className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle>Tell us about your lesson</CardTitle>
                    <CardDescription>Configure your quiz and assessment parameters</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Topic Category */}
                <div className="space-y-2">
                  <Label htmlFor="category">Topic Category</Label>
                  <Select value={topicCategory} onValueChange={setTopicCategory}>
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Select a category..." />
                    </SelectTrigger>
                    <SelectContent>
                      {topicCategories.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>
                          {cat.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Topic Input */}
                <div className="space-y-2">
                  <Label htmlFor="topic">Topic *</Label>
                  <Input
                    id="topic"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., The Maillard Reaction"
                    className="h-12"
                  />
                </div>

                {/* Grade Level */}
                <div className="space-y-3">
                  <Label>Grade Level</Label>
                  <RadioGroup
                    value={gradeLevel}
                    onValueChange={setGradeLevel}
                    className="flex flex-wrap gap-3"
                  >
                    {gradeLevels.map((level) => (
                      <div key={level.value} className="flex items-center">
                        <RadioGroupItem
                          value={level.value}
                          id={`grade-${level.value}`}
                          className="peer sr-only"
                        />
                        <Label
                          htmlFor={`grade-${level.value}`}
                          className="px-4 py-2 rounded-lg border border-input bg-background hover:bg-accent hover:text-accent-foreground cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/10 peer-data-[state=checked]:text-primary"
                        >
                          {level.label}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                </div>

                {/* Assessment Type */}
                <div className="space-y-2">
                  <Label htmlFor="assessmentType">Assessment Type</Label>
                  <Select value={assessmentType} onValueChange={setAssessmentType}>
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Select assessment type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {assessmentTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Number of Questions */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Number of Questions</Label>
                    <span className="text-sm font-medium text-primary">
                      {questionCount[0]} questions
                    </span>
                  </div>
                  <Slider
                    value={questionCount}
                    onValueChange={setQuestionCount}
                    min={1}
                    max={25}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1</span>
                    <span>25</span>
                  </div>
                </div>

                {/* Additional Details */}
                <div className="space-y-2">
                  <Label htmlFor="details">Add details (optional)</Label>
                  <Textarea
                    id="details"
                    value={additionalDetails}
                    onChange={(e) => setAdditionalDetails(e.target.value)}
                    placeholder="e.g., Focus on temperature control and time factors"
                    rows={3}
                    className="resize-none"
                  />
                </div>

                {/* Submit Button */}
                <Button
                  onClick={handleGenerate}
                  disabled={!topic.trim() || isLoading}
                  variant="warm"
                  size="lg"
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Assessment
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "200ms" }}>
            <OutputDisplay
              sections={output}
              isLoading={isLoading}
              onRegenerate={handleRegenerate}
              onSave={handleSave}
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default QuizAssessment;