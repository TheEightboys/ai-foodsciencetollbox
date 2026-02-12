import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  DollarSign, 
  TrendingUp, 
  CreditCard,
  Calendar,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Mock data for earnings
const mockTransactions = [
  {
    id: "1",
    date: "2024-01-15",
    product: "Food Chemistry Introduction - Lesson Starter",
    amount: 4.24, // after 15% commission
    status: "completed",
  },
  {
    id: "2",
    date: "2024-01-14",
    product: "Microbiology Lab Safety Guide",
    amount: 6.79,
    status: "completed",
  },
  {
    id: "3",
    date: "2024-01-13",
    product: "Food Chemistry Introduction - Lesson Starter",
    amount: 4.24,
    status: "completed",
  },
  {
    id: "4",
    date: "2024-01-12",
    product: "Nutrition Assessment Quiz Pack",
    amount: 5.09,
    status: "pending",
  },
];

const EarningsDashboard = () => {
  const totalEarnings = mockTransactions.reduce((sum, t) => sum + t.amount, 0);
  const pendingEarnings = mockTransactions
    .filter((t) => t.status === "pending")
    .reduce((sum, t) => sum + t.amount, 0);

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
            <DollarSign className="w-8 h-8 text-primary" />
            Earnings Dashboard
          </h1>
          <p className="text-muted-foreground">
            Track your marketplace earnings and payouts.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Earnings</p>
                  <p className="text-2xl font-bold">${totalEarnings.toFixed(2)}</p>
                  <p className="text-xs text-accent flex items-center gap-1 mt-1">
                    <ArrowUpRight className="w-3 h-3" />
                    +12% from last month
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-primary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">This Month</p>
                  <p className="text-2xl font-bold">$20.36</p>
                  <p className="text-xs text-accent flex items-center gap-1 mt-1">
                    <ArrowUpRight className="w-3 h-3" />
                    +8% from last month
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-accent/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending</p>
                  <p className="text-2xl font-bold">${pendingEarnings.toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Processing...
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-secondary/60" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Next Payout</p>
                  <p className="text-2xl font-bold">Jan 31</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    ~$25.45 estimated
                  </p>
                </div>
                <CreditCard className="w-8 h-8 text-muted-foreground/60" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Commission Info */}
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <DollarSign className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Platform Commission</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  A 15% platform commission is deducted from each sale to cover payment processing, hosting, and platform maintenance. 
                  The amounts shown are your net earnings after commission.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Your latest sales and earnings</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockTransactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell className="text-muted-foreground">
                      {new Date(transaction.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="font-medium">{transaction.product}</TableCell>
                    <TableCell className="font-semibold text-accent">
                      +${transaction.amount.toFixed(2)}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={transaction.status === "completed" ? "default" : "secondary"}
                      >
                        {transaction.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Payout Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Payout Settings</CardTitle>
            <CardDescription>Configure how you receive your earnings</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Payout settings will be available in a future update. 
              You'll be able to connect your bank account or PayPal for automatic payouts.
            </p>
            <Button variant="outline" disabled>
              Configure Payouts
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default EarningsDashboard;
