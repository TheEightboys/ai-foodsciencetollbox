import { useState } from "react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { 
  ArrowLeft, 
  Store, 
  Search, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Star,
  Package
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Mock data for products
const mockProducts = [
  {
    id: "1",
    title: "Food Chemistry Introduction - Lesson Starter",
    status: "published",
    price: 4.99,
    sales: 23,
    rating: 4.8,
    views: 156,
  },
  {
    id: "2",
    title: "Microbiology Lab Safety Guide",
    status: "published",
    price: 7.99,
    sales: 15,
    rating: 4.5,
    views: 89,
  },
  {
    id: "3",
    title: "Nutrition Assessment Quiz Pack",
    status: "draft",
    price: 5.99,
    sales: 0,
    rating: 0,
    views: 0,
  },
];

const MyShop = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredProducts = mockProducts.filter((product) =>
    product.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            <Store className="w-8 h-8 text-primary" />
            My Shop
          </h1>
          <p className="text-muted-foreground">
            Manage your products and shop settings.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Products</p>
                  <p className="text-2xl font-bold">{mockProducts.length}</p>
                </div>
                <Package className="w-8 h-8 text-primary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Published</p>
                  <p className="text-2xl font-bold">
                    {mockProducts.filter((p) => p.status === "published").length}
                  </p>
                </div>
                <Eye className="w-8 h-8 text-accent/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Sales</p>
                  <p className="text-2xl font-bold">
                    {mockProducts.reduce((sum, p) => sum + p.sales, 0)}
                  </p>
                </div>
                <Star className="w-8 h-8 text-secondary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Rating</p>
                  <p className="text-2xl font-bold">
                    {(
                      mockProducts.filter((p) => p.rating > 0).reduce((sum, p) => sum + p.rating, 0) /
                      mockProducts.filter((p) => p.rating > 0).length || 0
                    ).toFixed(1)}
                  </p>
                </div>
                <Star className="w-8 h-8 text-yellow-500/60" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Products Table */}
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <CardTitle>Your Products</CardTitle>
                <CardDescription>Manage all your marketplace listings</CardDescription>
              </div>
              <div className="flex gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 w-64"
                  />
                </div>
                <Button asChild>
                  <Link to="/marketplace/upload">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Product
                  </Link>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Sales</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Views</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell className="font-medium">{product.title}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={product.status === "published" ? "default" : "secondary"}
                      >
                        {product.status}
                      </Badge>
                    </TableCell>
                    <TableCell>${product.price.toFixed(2)}</TableCell>
                    <TableCell>{product.sales}</TableCell>
                    <TableCell>
                      {product.rating > 0 ? (
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          {product.rating}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>{product.views}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="icon">
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="text-destructive">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default MyShop;
