import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, CreditCard, Calendar, Loader2, Zap, Star, Sparkles } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { membershipService } from '@/lib/api/memberships';
import { paymentService } from '@/lib/api/payments';
import { MEMBERSHIP_TIERS } from '@/lib/constants';
import { format } from 'date-fns';
import { useToast } from '@/hooks/use-toast';

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

type SubscriptionTier = 'trial' | 'starter' | 'pro';

interface ProfileData {
  subscription_tier: SubscriptionTier | null;
  generation_count: number | null;
  generation_limit: number | null;
  subscription_start_date: string | null;
  subscription_end_date: string | null;
  billing_interval: 'month' | 'year' | null;
}

export default function Billing() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loadingPortal, setLoadingPortal] = useState(false);

  const tierIcons: Record<string, React.ReactNode> = {
    trial: <Sparkles className="h-5 w-5" />,
    starter: <Zap className="h-5 w-5" />,
    pro: <Star className="h-5 w-5" />,
  };

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;
      
      try {
        const membership = await membershipService.getCurrentMembership();
        // Handle generation_limit: null means unlimited, convert to -1 for frontend
        const generationLimit = membership.tier.generation_limit === null 
          ? -1  // -1 means unlimited in frontend
          : (membership.tier.generation_limit ?? 10);
        
        // Calculate billing interval from period dates if not provided
        let billingInterval: 'month' | 'year' | null = membership.billing_interval || null;
        if (!billingInterval && membership.current_period_start && membership.current_period_end) {
          const startDate = new Date(membership.current_period_start);
          const endDate = new Date(membership.current_period_end);
          const daysDiff = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
          // If period is around 365 days, it's yearly; otherwise monthly
          if (daysDiff >= 300) {
            billingInterval = 'year';
          } else if (daysDiff >= 25) {
            billingInterval = 'month';
          }
        }
        
        // Determine if this is a paid subscription (has Stripe subscription ID)
        const isPaidSubscription = !!membership.stripe_subscription_id && membership.tier.name !== 'trial';
        
        setProfile({
          subscription_tier: membership.tier.name.toLowerCase() as SubscriptionTier,
          generation_count: membership.generations_used_this_month,
          generation_limit: generationLimit,
          subscription_start_date: membership.current_period_start,
          subscription_end_date: membership.current_period_end,
          billing_interval: isPaidSubscription ? billingInterval : null, // Only set interval for paid subscriptions
        });
      } catch (error) {
        // Error handled silently
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [user]);

  const currentTier = profile?.subscription_tier || 'trial';
  const tierKey = currentTier.toUpperCase() as keyof typeof MEMBERSHIP_TIERS;
  const tierInfo = MEMBERSHIP_TIERS[tierKey] || MEMBERSHIP_TIERS.TRIAL;
  const generationsUsed = profile?.generation_count || 0;
  const generationsLimit = profile?.generation_limit === -1 ? null : (profile?.generation_limit ?? 10);
  const isUnlimited = profile?.generation_limit === -1;

  const handleManagePaymentMethod = async () => {
    setLoadingPortal(true);
    try {
      const returnUrl = `${window.location.origin}/account/billing`;
      const { portal_url } = await paymentService.createCustomerPortalSession(returnUrl);
      window.location.href = portal_url;
    } catch (error: any) {
      toast({
        title: 'Failed to open payment portal',
        description: error?.response?.data?.error || 'Unable to open payment management. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoadingPortal(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="space-y-6">
          {/* Current Plan Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-full">
                  <CreditCard className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Billing & Subscription</CardTitle>
                  <CardDescription>Manage your subscription and billing</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <>
                  {/* Current Plan */}
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-full bg-primary/10">
                          {tierIcons[currentTier]}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{tierInfo?.name || 'Trial'} Plan</h3>
                          <p className="text-sm text-muted-foreground">
                            {isUnlimited ? 'Unlimited generations' : `${generationsLimit} generations/month`}
                          </p>
                        </div>
                      </div>
                      <Badge variant={currentTier === 'trial' ? 'secondary' : 'default'}>
                        {currentTier === 'trial' ? 'Free' : 'Active'}
                      </Badge>
                    </div>

                    {/* Usage Progress */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Generations used</span>
                        <span className="font-medium">
                          {isUnlimited ? `${generationsUsed} used` : `${generationsUsed} / ${generationsLimit}`}
                        </span>
                      </div>
                      {!isUnlimited && (
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${Math.min((generationsUsed / generationsLimit) * 100, 100)}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Subscription Dates */}
                  {safeFormatDate(profile?.subscription_start_date || null, 'MMMM d, yyyy') && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      <span>
                        Started: {safeFormatDate(profile?.subscription_start_date || null, 'MMMM d, yyyy')}
                      </span>
                    </div>
                  )}
                  {safeFormatDate(profile?.subscription_end_date || null, 'MMMM d, yyyy') && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
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

                  {/* Actions */}
                  <div className="flex flex-col gap-3">
                    <Button onClick={() => navigate('/pricing')} className="w-full">
                      {currentTier === 'trial' ? 'Upgrade Plan' : 'Change Plan'}
                    </Button>
                    {currentTier !== 'trial' && (
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={handleManagePaymentMethod}
                        disabled={loadingPortal}
                      >
                        {loadingPortal ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Opening...
                          </>
                        ) : (
                          'Manage Payment Method'
                        )}
                      </Button>
                    )}
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Your Plan Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {(tierInfo?.features || []).map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="text-accent">✓</span>
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
