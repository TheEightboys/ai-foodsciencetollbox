import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Settings, Users, DollarSign, Shield, Plus, Search, Loader2, Mail } from "lucide-react";
import { MEMBERSHIP_TIERS } from "@/lib/constants";
import { toast } from "@/hooks/use-toast";
import apiClient from "@/lib/api/client";

type TierKey = keyof typeof MEMBERSHIP_TIERS;

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  is_active: boolean;
  membership_tier: string | null;
  membership_status: string | null;
}

const Admin = () => {
  const [tiers, setTiers] = useState(MEMBERSHIP_TIERS);
  const [commissionRate, setCommissionRate] = useState("15");
  const [users, setUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [showCreateUserDialog, setShowCreateUserDialog] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserFirstName, setNewUserFirstName] = useState("");
  const [newUserLastName, setNewUserLastName] = useState("");
  const [newUserTier, setNewUserTier] = useState("trial");
  const [isCreatingUser, setIsCreatingUser] = useState(false);

  const handleUpdatePricing = (tierKey: TierKey, field: "monthly" | "yearly" | "oneTime", value: number) => {
    const tier = tiers[tierKey];
    if (!tier) return;
    
    setTiers((prev) => ({
      ...prev,
      [tierKey]: {
        ...tier,
        price: {
          ...tier.price,
          [field]: value,
        },
      },
    }));
    toast({
      title: "Pricing updated",
      description: `${tier.name} tier pricing has been updated.`,
    });
  };

  const handleUpdateGenerations = (tierKey: TierKey, value: number) => {
    const tier = tiers[tierKey];
    if (!tier) return;
    
    setTiers((prev) => ({
      ...prev,
      [tierKey]: {
        ...tier,
        generations: value,
      },
    }));
    toast({
      title: "Generation limit updated",
      description: `${tier.name} tier generation limit has been updated.`,
    });
  };

  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    try {
      const response = await apiClient.get('/admin-dashboard/users/', {
        params: searchQuery ? { search: searchQuery } : {}
      });
      setUsers(response.data.results || response.data);
    } catch (error: any) {
      toast({
        title: "Failed to load users",
        description: error?.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    } finally {
      setIsLoadingUsers(false);
    }
  };

  // Fetch users with debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers();
    }, searchQuery ? 500 : 0); // Immediate fetch if search is empty, debounce if typing

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserEmail.trim()) {
      toast({
        title: "Email required",
        description: "Please enter an email address",
        variant: "destructive",
      });
      return;
    }

    setIsCreatingUser(true);
    try {
      const response = await apiClient.post('/admin-dashboard/users/create/', {
        email: newUserEmail.trim(),
        first_name: newUserFirstName.trim(),
        last_name: newUserLastName.trim(),
        tier_name: newUserTier,
      });
      
      toast({
        title: "User created",
        description: `User ${response.data.user.email} has been created successfully.`,
      });
      
      setShowCreateUserDialog(false);
      setNewUserEmail("");
      setNewUserFirstName("");
      setNewUserLastName("");
      setNewUserTier("trial");
      fetchUsers();
    } catch (error: any) {
      toast({
        title: "Failed to create user",
        description: error?.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    } finally {
      setIsCreatingUser(false);
    }
  };

  const handleAssignTier = async (userId: number, tierName: string) => {
    try {
      const response = await apiClient.post(`/admin-dashboard/users/${userId}/assign-membership/`, {
        tier_name: tierName,
      });
      
      toast({
        title: "Membership updated",
        description: response.data.message,
      });
      
      fetchUsers();
    } catch (error: any) {
      toast({
        title: "Failed to update membership",
        description: error?.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="animate-fade-in">
          <h1 className="font-serif text-2xl md:text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Shield className="w-8 h-8 text-primary" />
            Admin Dashboard
          </h1>
          <p className="text-muted-foreground">
            Manage membership tiers, pricing, and platform settings.
          </p>
        </div>

        <Tabs defaultValue="tiers" className="space-y-6">
          <TabsList>
            <TabsTrigger value="tiers">Membership Tiers</TabsTrigger>
            <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
            <TabsTrigger value="users">User Management</TabsTrigger>
          </TabsList>

          {/* Membership Tiers Tab */}
          <TabsContent value="tiers" className="space-y-6">
            {(Object.keys(tiers) as TierKey[]).map((key) => {
              const tier = tiers[key];
              return (
                <Card key={key}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{tier.name}</CardTitle>
                        <CardDescription>
                          {tier.generations === -1 ? "Unlimited" : `${tier.generations} generations/month`}
                        </CardDescription>
                      </div>
                      <Badge variant="secondary">Active</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-3">
                      {'monthly' in tier.price && (
                        <div className="space-y-2">
                          <Label>Monthly Price ($)</Label>
                          <Input
                            type="number"
                            value={tier.price.monthly}
                            onChange={(e) => handleUpdatePricing(key, "monthly", parseFloat(e.target.value) || 0)}
                          />
                        </div>
                      )}
                      {'yearly' in tier.price && (
                        <div className="space-y-2">
                          <Label>Yearly Price ($)</Label>
                          <Input
                            type="number"
                            value={tier.price.yearly}
                            onChange={(e) => handleUpdatePricing(key, "yearly", parseFloat(e.target.value) || 0)}
                          />
                        </div>
                      )}
                      {'oneTime' in tier.price && (
                        <div className="space-y-2">
                          <Label>One-Time Price ($)</Label>
                          <Input
                            type="number"
                            value={tier.price.oneTime}
                            onChange={(e) => handleUpdatePricing(key, "oneTime", parseFloat(e.target.value) || 0)}
                          />
                        </div>
                      )}
                      {tier.generations !== -1 && (
                        <div className="space-y-2">
                          <Label>Generation Limit</Label>
                          <Input
                            type="number"
                            value={tier.generations}
                            onChange={(e) => handleUpdateGenerations(key, parseInt(e.target.value) || 0)}
                          />
                        </div>
                      )}
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <Label className="text-sm font-medium">Tier Visibility</Label>
                        <p className="text-xs text-muted-foreground">
                          {key === "TRIAL" || key === "FOUNDERS" 
                            ? "Hidden by default (promotional tiers)"
                            : "Visible to all users"}
                        </p>
                      </div>
                      <Switch defaultChecked={key !== "TRIAL" && key !== "FOUNDERS"} />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </TabsContent>

          {/* Marketplace Tab */}
          <TabsContent value="marketplace" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Marketplace Settings</CardTitle>
                <CardDescription>Configure marketplace commission and approval settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="commission">Commission Rate (%)</Label>
                  <Input
                    id="commission"
                    type="number"
                    value={commissionRate}
                    onChange={(e) => setCommissionRate(e.target.value)}
                    className="max-w-xs"
                  />
                  <p className="text-sm text-muted-foreground">
                    Percentage of each sale that goes to the platform
                  </p>
                </div>
                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div>
                    <Label className="text-sm font-medium">Require Approval for New Products</Label>
                    <p className="text-xs text-muted-foreground">
                      When enabled, all new products require admin approval before publishing
                    </p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div>
                    <Label className="text-sm font-medium">Auto-Publish by Default</Label>
                    <p className="text-xs text-muted-foreground">
                      Products are published immediately unless flagged for review
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* User Management Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>Add users and assign subscription plans</CardDescription>
                  </div>
                  <Button onClick={() => setShowCreateUserDialog(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add User
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search users by email or name..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {isLoadingUsers ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                  ) : users.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No users found
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {users.map((user) => (
                        <Card key={user.id} className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <Mail className="h-4 w-4 text-muted-foreground" />
                                <span className="font-medium">{user.email}</span>
                                {!user.is_active && (
                                  <Badge variant="secondary">Inactive</Badge>
                                )}
                              </div>
                              {(user.first_name || user.last_name) && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  {user.first_name} {user.last_name}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-2">
                                <Badge variant="outline">
                                  {user.membership_tier || "No membership"}
                                </Badge>
                                {user.membership_status && (
                                  <Badge variant="secondary">
                                    {user.membership_status}
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Select
                                value={user.membership_tier?.toLowerCase() || "trial"}
                                onValueChange={(value) => handleAssignTier(user.id, value)}
                              >
                                <SelectTrigger className="w-[140px]">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="trial">Trial</SelectItem>
                                  <SelectItem value="starter">Starter</SelectItem>
                                  <SelectItem value="pro">Pro</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create User Dialog */}
      <Dialog open={showCreateUserDialog} onOpenChange={setShowCreateUserDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
            <DialogDescription>
              Create a new user account and assign a subscription plan
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateUser} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                placeholder="user@example.com"
                value={newUserEmail}
                onChange={(e) => setNewUserEmail(e.target.value)}
                required
                disabled={isCreatingUser}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  type="text"
                  placeholder="First name"
                  value={newUserFirstName}
                  onChange={(e) => setNewUserFirstName(e.target.value)}
                  disabled={isCreatingUser}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  type="text"
                  placeholder="Last name"
                  value={newUserLastName}
                  onChange={(e) => setNewUserLastName(e.target.value)}
                  disabled={isCreatingUser}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="tier">Subscription Plan</Label>
              <Select value={newUserTier} onValueChange={setNewUserTier} disabled={isCreatingUser}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="trial">Trial</SelectItem>
                  <SelectItem value="starter">Starter</SelectItem>
                  <SelectItem value="pro">Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowCreateUserDialog(false);
                  setNewUserEmail("");
                  setNewUserFirstName("");
                  setNewUserLastName("");
                  setNewUserTier("trial");
                }}
                disabled={isCreatingUser}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreatingUser}>
                {isCreatingUser ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create User
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default Admin;

