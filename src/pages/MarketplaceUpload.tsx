import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Upload, Sparkles, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

const MarketplaceUpload = () => {
  const [productTitle, setProductTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [longDescription, setLongDescription] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [price, setPrice] = useState("");
  const [uploadType, setUploadType] = useState<"shop" | "free-hub">("shop");
  const [autoPublish, setAutoPublish] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Auto-generate product details from favorite content
  const handleAutoGenerate = async () => {
    setIsGenerating(true);
    // Simulate AI generation
    setTimeout(() => {
      setProductTitle("Food Chemistry Introduction - Lesson Starter");
      setShortDescription("Engaging lesson starter for introducing food chemistry concepts to high school students.");
      setLongDescription("This comprehensive lesson starter provides teachers with an engaging introduction to food chemistry. It includes attention-grabbing hooks, real-world connections, and key questions to spark student interest. Perfect for high school food science courses.");
      setTags(["food-chemistry", "lesson-starter", "high-school", "introduction"]);
      setPrice("4.99");
      setIsGenerating(false);
      toast({
        title: "Details generated!",
        description: "Product details have been auto-generated. Review and edit as needed.",
      });
    }, 1500);
  };

  const handleUpload = async () => {
    if (!productTitle.trim() || !shortDescription.trim() || (uploadType === "shop" && !price)) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    // Simulate upload
    setTimeout(() => {
      setIsUploading(false);
      toast({
        title: "Upload successful!",
        description: autoPublish 
          ? "Your product has been published to the marketplace."
          : "Your product has been submitted for review.",
      });
    }, 2000);
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
            <Upload className="w-8 h-8 text-primary" />
            Upload to Marketplace
          </h1>
          <p className="text-muted-foreground">
            Share your best teaching materials with other educators or add them to the Free Resource Hub.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Product Information</CardTitle>
                    <CardDescription>Auto-generate details or fill them in manually</CardDescription>
                  </div>
                  <Button variant="outline" onClick={handleAutoGenerate} disabled={isGenerating}>
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Auto-Generate
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Upload Type */}
                <div className="space-y-3">
                  <Label>Upload To</Label>
                  <RadioGroup value={uploadType} onValueChange={(v) => setUploadType(v as "shop" | "free-hub")}>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="shop" id="shop" />
                      <Label htmlFor="shop" className="cursor-pointer">
                        My Shop (Sell)
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="free-hub" id="free-hub" />
                      <Label htmlFor="free-hub" className="cursor-pointer">
                        Free Resource Hub (Share)
                      </Label>
                    </div>
                  </RadioGroup>
                </div>

                {/* Product Title */}
                <div className="space-y-2">
                  <Label htmlFor="title">Product Title *</Label>
                  <Input
                    id="title"
                    value={productTitle}
                    onChange={(e) => setProductTitle(e.target.value)}
                    placeholder="Auto-generated product title..."
                    className="h-12"
                  />
                </div>

                {/* Short Description */}
                <div className="space-y-2">
                  <Label htmlFor="shortDesc">Short Description *</Label>
                  <Textarea
                    id="shortDesc"
                    value={shortDescription}
                    onChange={(e) => setShortDescription(e.target.value)}
                    placeholder="Auto-generated short description..."
                    rows={2}
                    className="resize-none"
                  />
                </div>

                {/* Long Description */}
                <div className="space-y-2">
                  <Label htmlFor="longDesc">Long Description *</Label>
                  <Textarea
                    id="longDesc"
                    value={longDescription}
                    onChange={(e) => setLongDescription(e.target.value)}
                    placeholder="Auto-generated detailed description..."
                    rows={5}
                    className="resize-none"
                  />
                </div>

                {/* Tags */}
                <div className="space-y-2">
                  <Label>Tags</Label>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="cursor-pointer">
                        {tag}
                        <button
                          onClick={() => setTags(tags.filter((_, i) => i !== index))}
                          className="ml-2 hover:text-destructive"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add a tag and press Enter..."
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && e.currentTarget.value.trim()) {
                        setTags([...tags, e.currentTarget.value.trim()]);
                        e.currentTarget.value = "";
                      }
                    }}
                    className="h-12"
                  />
                </div>

                {/* Price (only for shop) */}
                {uploadType === "shop" && (
                  <div className="space-y-2">
                    <Label htmlFor="price">Price ($) *</Label>
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      min="0"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      placeholder="Auto-suggested price..."
                      className="h-12"
                    />
                  </div>
                )}

                {/* Auto-Publish Toggle */}
                <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="autoPublish">Auto-Publish</Label>
                    <p className="text-sm text-muted-foreground">
                      {autoPublish 
                        ? "Product will be published immediately (admin can require approval later if needed)"
                        : "Product will require admin approval before publishing"}
                    </p>
                  </div>
                  <Switch
                    id="autoPublish"
                    checked={autoPublish}
                    onCheckedChange={setAutoPublish}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upload Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="font-medium">
                      {uploadType === "shop" ? "My Shop" : "Free Resource Hub"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Publishing:</span>
                    <span className="font-medium">
                      {autoPublish ? "Auto-Publish" : "Requires Approval"}
                    </span>
                  </div>
                  {uploadType === "shop" && price && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Price:</span>
                      <span className="font-medium">${price}</span>
                    </div>
                  )}
                </div>
                <Button
                  onClick={handleUpload}
                  disabled={isUploading || !productTitle.trim() || !shortDescription.trim() || (uploadType === "shop" && !price)}
                  variant="warm"
                  size="lg"
                  className="w-full"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      Upload Product
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tips</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <p>• Use the Auto-Generate button to quickly create product details from your content</p>
                <p>• Review and edit auto-generated fields to match your style</p>
                <p>• Add relevant tags to help teachers find your product</p>
                <p>• Products in the Free Resource Hub are available to Pro and Unlimited tier members</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MarketplaceUpload;

