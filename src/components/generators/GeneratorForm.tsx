import { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Sparkles, Loader2 } from "lucide-react";

interface GeneratorFormProps {
  title: string;
  description: string;
  icon: ReactNode;
  // NEW CONSOLIDATED DESIGN: Single prompt with user_intent
  userIntent?: string;
  onUserIntentChange?: (value: string) => void;
  numObjectives?: number;
  onNumObjectivesChange?: (value: number) => void;
  
  // LEGACY PROPS: For backward compatibility
  learningGoal?: string;
  onLearningGoalChange?: (value: string) => void;
  gradeLevel: string;
  onGradeLevelChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  userIntentPlaceholder?: string;
  learningGoalPlaceholder?: string;
  submitLabel?: string;
  children?: ReactNode;
}

const gradeLevels = GRADE_LEVELS;

import { GRADE_LEVELS } from "@/lib/constants";

export function GeneratorForm({
  title,
  description,
  icon,
  // NEW CONSOLIDATED DESIGN: Use userIntent if provided, fallback to learningGoal
  userIntent,
  onUserIntentChange,
  numObjectives = 5,
  onNumObjectivesChange,
  learningGoal,
  onLearningGoalChange,
  gradeLevel,
  onGradeLevelChange,
  onSubmit,
  isLoading,
  userIntentPlaceholder = "What do you want students to learn or be able to do?",
  learningGoalPlaceholder = "What do you want students to learn or be able to do?",
  submitLabel = "Generate Content",
  children,
}: GeneratorFormProps) {
  // Use new consolidated design if available, fallback to legacy
  const currentIntent = userIntent || learningGoal || "";
  const currentIntentChange = onUserIntentChange || onLearningGoalChange;
  const currentPlaceholder = userIntent ? userIntentPlaceholder : learningGoalPlaceholder;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center">
            {icon}
          </div>
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Grade Level at Top */}
        <div className="space-y-3">
          <Label>Grade Level</Label>
          <RadioGroup
            value={gradeLevel}
            onValueChange={onGradeLevelChange}
            className="flex flex-wrap gap-3"
          >
            {gradeLevels.map((level) => (
              <div key={level.value} className="flex items-center">
                <RadioGroupItem
                  value={level.value}
                  id={level.value}
                  className="peer sr-only"
                />
                <Label
                  htmlFor={level.value}
                  className="px-4 py-2 rounded-lg border border-input bg-background hover:bg-accent hover:text-accent-foreground cursor-pointer transition-all peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/10 peer-data-[state=checked]:text-primary"
                >
                  {level.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Single Prompt Input */}
        <div className="space-y-2">
          <Label htmlFor="learning-goal">
            {userIntent ? "What do you want students to learn or be able to do? *" : "What do you want students to learn or be able to do? *"}
          </Label>
          <Textarea
            id="learning-goal"
            value={currentIntent}
            onChange={(e) => currentIntentChange && currentIntentChange(e.target.value)}
            placeholder={currentPlaceholder}
            rows={4}
            className="resize-none"
          />
          <p className="text-sm text-muted-foreground">
            Be specific about the learning goals. Include context like grade level, subject, and specific skills.
          </p>
        </div>

        {/* Number of Objectives (NEW CONSOLIDATED FEATURE) */}
        {onNumObjectivesChange && (
          <div className="space-y-3">
            <Label>Number of Objectives</Label>
            <Slider
              value={[numObjectives]}
              onValueChange={(value) => onNumObjectivesChange(value[0])}
              max={10}
              min={4}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>4 objectives</span>
              <span>{numObjectives} selected</span>
              <span>10 objectives</span>
            </div>
          </div>
        )}

        {/* Additional form fields */}
        {children}

        {/* Submit Button */}
        <Button
          onClick={onSubmit}
          disabled={!currentIntent.trim() || isLoading}
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
              {submitLabel}
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}