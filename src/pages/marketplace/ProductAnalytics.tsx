import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  BarChart3, 
  Eye,
  ShoppingCart,
  Star,
  TrendingUp,
  Users
} from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// Mock data for analytics
const mockProductStats = [
  {
    id: "1",
    title: "Food Chemistry Introduction - Lesson Starter",
    views: 156,
    viewsTrend: 12,
    sales: 23,
    salesTrend: 8,
    revenue: 97.52,
    rating: 4.8,
    reviews: 18,
  },
  {
    id: "2",
    title: "Microbiology Lab Safety Guide",
    views: 89,
    viewsTrend: -3,
    sales: 15,
    salesTrend: 5,
    revenue: 101.93,
    rating: 4.5,
    reviews: 12,
  },
  {
    id: "3",
    title: "Nutrition Assessment Quiz Pack",
    views: 45,
    viewsTrend: 25,
    sales: 8,
    salesTrend: 15,
    revenue: 40.72,
    rating: 4.9,
    reviews: 6,
  },
];

const ProductAnalytics = () => {
  const totalViews = mockProductStats.reduce((sum, p) => sum + p.views, 0);
  const totalSales = mockProductStats.reduce((sum, p) => sum + p.sales, 0);
  const totalRevenue = mockProductStats.reduce((sum, p) => sum + p.revenue, 0);
  const avgConversion = totalViews > 0 ? ((totalSales / totalViews) * 100).toFixed(1) : "0";

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

        <div className="animate-fade-in flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-serif text-2xl md:text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-primary" />
              Product Analytics
            </h1>
            <p className="text-muted-foreground">
              View detailed analytics for your products.
            </p>
          </div>
          <Select defaultValue="30">
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Time period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Overview Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Views</p>
                  <p className="text-2xl font-bold">{totalViews}</p>
                  <p className="text-xs text-accent flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +15% vs last period
                  </p>
                </div>
                <Eye className="w-8 h-8 text-primary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Sales</p>
                  <p className="text-2xl font-bold">{totalSales}</p>
                  <p className="text-xs text-accent flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +9% vs last period
                  </p>
                </div>
                <ShoppingCart className="w-8 h-8 text-accent/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Revenue</p>
                  <p className="text-2xl font-bold">${totalRevenue.toFixed(2)}</p>
                  <p className="text-xs text-accent flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +12% vs last period
                  </p>
                </div>
                <BarChart3 className="w-8 h-8 text-secondary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Conversion</p>
                  <p className="text-2xl font-bold">{avgConversion}%</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Views to sales
                  </p>
                </div>
                <Users className="w-8 h-8 text-muted-foreground/60" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Product Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Product Performance</CardTitle>
            <CardDescription>Detailed breakdown by product</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {mockProductStats.map((product) => (
              <div key={product.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                  <h3 className="font-semibold">{product.title}</h3>
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                    <span className="text-sm font-medium">{product.rating}</span>
                    <span className="text-sm text-muted-foreground">({product.reviews} reviews)</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Views</p>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-semibold">{product.views}</span>
                      <Badge 
                        variant={product.viewsTrend > 0 ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {product.viewsTrend > 0 ? "+" : ""}{product.viewsTrend}%
                      </Badge>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Sales</p>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-semibold">{product.sales}</span>
                      <Badge 
                        variant={product.salesTrend > 0 ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {product.salesTrend > 0 ? "+" : ""}{product.salesTrend}%
                      </Badge>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Revenue</p>
                    <span className="text-lg font-semibold text-accent">
                      ${product.revenue.toFixed(2)}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Conversion</p>
                    <span className="text-lg font-semibold">
                      {((product.sales / product.views) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Charts Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Sales Trends</CardTitle>
            <CardDescription>Visual analytics coming soon</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-muted/30 rounded-lg border-2 border-dashed">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">
                  Interactive charts and analytics will be available in a future update.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default ProductAnalytics;
