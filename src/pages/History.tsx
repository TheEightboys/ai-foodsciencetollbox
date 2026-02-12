import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Search,
  Eye,
  Copy,
  Trash2,
  History as HistoryIcon,
  BookOpen,
  Target,
  Clock,
  Check,
  Download,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface HistoryItem {
  id: string;
  type: "lesson" | "objectives" | "bellringer";
  title: string;
  preview: string;
  content: string;
  gradeLevel: string;
  createdAt: string;
}

const mockHistory: HistoryItem[] = [
  {
    id: "1",
    type: "lesson",
    title: "Maillard Reaction Lesson Starter",
    preview: "Have you ever wondered why a grilled steak tastes completely different from a boiled one...",
    content: "Have you ever wondered why a grilled steak tastes completely different from a boiled one? Or why toast smells so amazing? The answer lies in one of food science's most fascinating transformations: the Maillard Reaction.\n\nNamed after French chemist Louis-Camille Maillard, this chemical reaction occurs when proteins and sugars are heated together. It's responsible for the brown color and complex flavors in roasted coffee, toasted bread, grilled meats, and even French fries.\n\nKey Discussion Points:\n1. What foods can you think of that undergo browning when cooked?\n2. Why do you think temperature matters in this reaction?\n3. How might understanding this reaction help us become better cooks?",
    gradeLevel: "High School",
    createdAt: "Dec 2, 2025 at 2:30 PM",
  },
  {
    id: "2",
    type: "objectives",
    title: "Food Safety Learning Objectives",
    preview: "Students will be able to identify the four danger zones...",
    content: "By the end of this lesson, students will be able to:\n\n1. Identify the four key temperature danger zones for food safety (40°F-140°F)\n2. Explain the importance of proper handwashing techniques in preventing foodborne illness\n3. Describe the correct methods for storing raw and cooked foods\n4. List at least five common foodborne pathogens and their sources\n5. Demonstrate proper food handling procedures during food preparation\n6. Analyze real-world scenarios to identify potential food safety hazards",
    gradeLevel: "Middle School",
    createdAt: "Dec 1, 2025 at 3:42 PM",
  },
  {
    id: "3",
    type: "bellringer",
    title: "Carbohydrates Bell Ringer",
    preview: "Quick Question: Think about carbohydrates - what's one thing you already know...",
    content: "Quick Question: Think about carbohydrates - what's one thing you already know about them?\n\nWarm-Up Activity (3 minutes):\nLook at your breakfast this morning (or imagine what you typically eat). List at least three foods that contain carbohydrates. For each food, try to guess whether it contains simple or complex carbohydrates.\n\nBonus Challenge:\nWhy do athletes often 'carb load' before a big event? Write your hypothesis in 1-2 sentences.",
    gradeLevel: "High School",
    createdAt: "Dec 1, 2025 at 9:15 AM",
  },
  {
    id: "4",
    type: "lesson",
    title: "Fermentation Process Introduction",
    preview: "What do bread, yogurt, and kimchi all have in common? They all rely on...",
    content: "What do bread, yogurt, and kimchi all have in common? They all rely on one of the oldest biotechnological processes known to humanity: fermentation.\n\nFermentation is a metabolic process where microorganisms like bacteria and yeast convert sugars into other products like alcohol, acids, or gases. This process has been used for thousands of years to preserve food, enhance flavors, and create new food products.\n\nTypes of Fermentation:\n1. Alcoholic fermentation - used in beer, wine, and bread\n2. Lactic acid fermentation - used in yogurt, cheese, and sauerkraut\n3. Acetic acid fermentation - used in vinegar production\n\nDiscussion: What fermented foods have you eaten recently?",
    gradeLevel: "College",
    createdAt: "Nov 30, 2025 at 11:20 AM",
  },
  {
    id: "5",
    type: "objectives",
    title: "Nutrition Labels Objectives",
    preview: "Students will be able to read and interpret nutrition labels...",
    content: "By the end of this lesson, students will be able to:\n\n1. Read and interpret nutrition labels on food packages\n2. Calculate daily value percentages for key nutrients\n3. Compare nutrition information between similar products\n4. Identify hidden sugars and sodium in processed foods\n5. Make informed decisions about food choices based on nutritional information\n6. Explain the significance of serving sizes in nutrition calculations",
    gradeLevel: "Middle School",
    createdAt: "Nov 29, 2025 at 2:15 PM",
  },
];

const typeIcons = {
  lesson: <BookOpen className="w-5 h-5 text-primary" />,
  objectives: <Target className="w-5 h-5 text-primary" />,
  bellringer: <Clock className="w-5 h-5 text-primary" />,
};

const typeLabels = {
  lesson: "Lesson Starter",
  objectives: "Learning Objectives",
  bellringer: "Bell Ringer",
};

const History = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [timeFilter, setTimeFilter] = useState("all");
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filteredHistory = mockHistory.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.preview.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === "all" || item.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleCopy = (item: HistoryItem) => {
    navigator.clipboard.writeText(item.content);
    setCopiedId(item.id);
    toast({
      title: "Copied to clipboard",
      description: `"${item.title}" has been copied.`,
    });
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleView = (item: HistoryItem) => {
    setSelectedItem(item);
  };

  const handleDelete = (item: HistoryItem) => {
    toast({
      title: "Item deleted",
      description: `"${item.title}" has been removed from history.`,
    });
  };

  return (
    <>
      {/* View Content Dialog */}
      <Dialog open={!!selectedItem} onOpenChange={() => setSelectedItem(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedItem && typeIcons[selectedItem.type]}
              {selectedItem?.title}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
              <Badge variant="secondary">{selectedItem && typeLabels[selectedItem.type]}</Badge>
              <span>•</span>
              <span>{selectedItem?.gradeLevel}</span>
              <span>•</span>
              <span>{selectedItem?.createdAt}</span>
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
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    
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
            <HistoryIcon className="w-8 h-8 text-primary" />
            Generation History
          </h1>
          <p className="text-muted-foreground">
            View and manage all your previously generated content.
          </p>
        </div>

        {/* Filters */}
        <Card className="animate-slide-up" style={{ animationDelay: "100ms" }}>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search history..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="lesson">Lesson Starters</SelectItem>
                  <SelectItem value="objectives">Learning Objectives</SelectItem>
                  <SelectItem value="bellringer">Bell Ringers</SelectItem>
                </SelectContent>
              </Select>
              <Select value={timeFilter} onValueChange={setTimeFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="All Time" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Time</SelectItem>
                  <SelectItem value="7days">Last 7 Days</SelectItem>
                  <SelectItem value="30days">Last 30 Days</SelectItem>
                  <SelectItem value="90days">Last 90 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* History List */}
        <div className="space-y-3">
          {filteredHistory.map((item, index) => (
            <Card
              key={item.id}
              className="animate-slide-up hover:shadow-card-hover transition-shadow"
              style={{ animationDelay: `${(index + 2) * 50}ms` }}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center shrink-0">
                    {typeIcons[item.type]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold text-foreground mb-1">
                          {item.title}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                          <span className="bg-muted px-2 py-0.5 rounded">
                            {typeLabels[item.type]}
                          </span>
                          <span>·</span>
                          <span>{item.gradeLevel}</span>
                          <span>·</span>
                          <span>{item.createdAt}</span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {item.preview}
                        </p>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleView(item)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(item)}
                        >
                          {copiedId === item.id ? (
                            <Check className="w-4 h-4 text-green-500" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(item)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {filteredHistory.length === 0 && (
            <Card className="border-dashed">
              <CardContent className="p-12 text-center">
                <HistoryIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="font-serif font-semibold text-lg mb-2">
                  No results found
                </h3>
                <p className="text-sm text-muted-foreground">
                  Try adjusting your search or filters.
                </p>
              </CardContent>
            </Card>
          )}

          {filteredHistory.length > 0 && (
            <Button variant="outline" className="w-full">
              Load More
            </Button>
          )}
        </div>
        </div>
      </DashboardLayout>
    </>
  );
};

export default History;
