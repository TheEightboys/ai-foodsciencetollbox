import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { MEMBERSHIP_TIERS } from '@/lib/constants';
import { Check, Sparkles, Zap, Star, ArrowLeft, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { membershipService } from '@/lib/api/memberships';

// Production-ready error handling - no console logging

export default function Pricing() {
  const [searchParams] = useSearchParams();
  const selectedPlan = searchParams.get('plan')?.toUpperCase();
  const [isYearly, setIsYearly] = useState(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();

  const tierIcons = {
    TRIAL: <Sparkles className="h-6 w-6" />,
    STARTER: <Zap className="h-6 w-6" />,
    PRO: <Star className="h-6 w-6" />,
  };

  const tierColors = {
    TRIAL: 'border-muted',
    STARTER: 'border-primary/30',
    PRO: 'border-accent/50',
  };

  const handleSelectPlan = async (tierKey: string) => {
    if (!user) {
      toast({
        title: 'Please sign in',
        description: 'You need to be signed in to select a plan.',
        variant: 'destructive',
      });
      return;
    }

    if (tierKey === 'TRIAL') {
      // For trial, just redirect to dashboard
      toast({
        title: 'Trial activated!',
        description: 'You now have access to 15 generations per month.',
      });
      navigate('/');
      return;
    }

    setLoadingPlan(tierKey);

    try {
      // Get tier ID from tier key
      let tiers;
      try {
        tiers = await membershipService.getMembershipTiers();
      } catch (error: any) {
        throw new Error('Failed to fetch subscription plans. Please try again.');
      }
      
      // Ensure tiers is an array
      if (!tiers || !Array.isArray(tiers) || tiers.length === 0) {
        throw new Error('Invalid tiers data received from server. Please try again or contact support.');
      }
      
      // Find tier by case-insensitive name match
      const tier = tiers.find(t => t.name.toLowerCase() === tierKey.toLowerCase());
      
      if (!tier) {
        const availableTiers = tiers.map(t => `${t.name} (${t.display_name})`).join(', ');
        throw new Error(
          `Subscription plan "${tierKey}" not found. ` +
          `Available plans: ${availableTiers || 'None - please contact support'}.`
        );
      }

      if (!tier.id) {
        throw new Error('Invalid tier data: missing tier ID');
      }

      // Call the Django API to upgrade membership and get checkout URL
      let result;
      try {
        result = await membershipService.upgradeMembership(tier.id);
      } catch (error: any) {
        const apiError = error?.response?.data?.error || error?.response?.data?.detail || error?.message;
        throw new Error(apiError || 'Failed to start checkout. Please try again or contact support.');
      }
      
      if (!result) {
        throw new Error('No response from server. Please try again.');
      }
      
      if (!result.checkout_url) {
        throw new Error('No checkout URL received from server. Please contact support.');
      }

      // Redirect to Stripe checkout
      window.location.href = result.checkout_url;
    } catch (error: any) {
      const errorMessage = error?.message || error?.response?.data?.error || error?.response?.data?.detail || 'Failed to start checkout. Please try again.';
      toast({
        title: 'Checkout failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoadingPlan(null);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Choose Your Plan
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-6">
              Unlock the full potential of AI-powered lesson planning. 
              Start free and upgrade as your needs grow.
            </p>
            
            {/* Yearly toggle */}
            <div className="flex items-center justify-center gap-3">
              <Label htmlFor="yearly-toggle" className={!isYearly ? 'font-semibold' : 'text-muted-foreground'}>
                Monthly
              </Label>
              <Switch
                id="yearly-toggle"
                checked={isYearly}
                onCheckedChange={setIsYearly}
              />
              <Label htmlFor="yearly-toggle" className={isYearly ? 'font-semibold' : 'text-muted-foreground'}>
                Yearly
                <span className="ml-2 text-xs bg-accent/20 text-accent px-2 py-0.5 rounded-full">
                  Save 2 months
                </span>
              </Label>
            </div>
          </div>
        </div>

        {/* Pricing Comparison Table */}
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left p-4 font-semibold">Feature</th>
                    <th className="text-center p-4 font-semibold">
                      <div className="flex flex-col items-center">
                        <span>7-Day Trial</span>
                        <span className="text-2xl font-bold text-foreground mt-1">$0</span>
                      </div>
                    </th>
                    <th className="text-center p-4 font-semibold bg-accent/10">
                      <div className="flex flex-col items-center">
                        <span>Starter</span>
                        <span className="text-2xl font-bold text-foreground mt-1">
                          ${isYearly ? MEMBERSHIP_TIERS.STARTER.price.yearly : MEMBERSHIP_TIERS.STARTER.price.monthly}
                        </span>
                        <span className="text-xs text-muted-foreground">/{isYearly ? 'year' : 'mo'}</span>
                      </div>
                    </th>
                    <th className="text-center p-4 font-semibold bg-primary/10">
                      <div className="flex flex-col items-center">
                        <span>Pro</span>
                        <span className="text-2xl font-bold text-foreground mt-1">
                          ${isYearly ? MEMBERSHIP_TIERS.PRO.price.yearly : MEMBERSHIP_TIERS.PRO.price.monthly}
                        </span>
                        <span className="text-xs text-muted-foreground">/{isYearly ? 'year' : 'mo'}</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-border">
                    <td className="p-4 font-medium">Generations</td>
                    <td className="p-4 text-center">{MEMBERSHIP_TIERS.TRIAL.generations}</td>
                    <td className="p-4 text-center bg-accent/5">{MEMBERSHIP_TIERS.STARTER.generations}</td>
                    <td className="p-4 text-center bg-primary/5">Unlimited</td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="p-4 font-medium">Word Downloads</td>
                    <td className="p-4 text-center"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                    <td className="p-4 text-center bg-accent/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                    <td className="p-4 text-center bg-primary/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="p-4 font-medium">Save & Manage Content in Dashboard</td>
                    <td className="p-4 text-center"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-accent/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                    <td className="p-4 text-center bg-primary/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="p-4 font-medium">Priority Support</td>
                    <td className="p-4 text-center"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-accent/5"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-primary/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                  </tr>
                  <tr className="border-b border-border">
                    <td className="p-4 font-medium">Early Access to New Tools</td>
                    <td className="p-4 text-center"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-accent/5"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-primary/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                  </tr>
                  <tr>
                    <td className="p-4 font-medium">Food Science Academy Membership</td>
                    <td className="p-4 text-center"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-accent/5"><span className="text-muted-foreground">✘</span></td>
                    <td className="p-4 text-center bg-primary/5"><Check className="h-5 w-5 mx-auto text-accent" /></td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td className="p-4"></td>
                    <td className="p-4">
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={() => handleSelectPlan('TRIAL')}
                        disabled={loadingPlan === 'TRIAL'}
                      >
                        {loadingPlan === 'TRIAL' ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          'Start Free Trial'
                        )}
                      </Button>
                    </td>
                    <td className="p-4 bg-accent/5">
                      <Button 
                        className="w-full"
                        onClick={() => handleSelectPlan('STARTER')}
                        disabled={loadingPlan === 'STARTER'}
                      >
                        {loadingPlan === 'STARTER' ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          'Get Started'
                        )}
                      </Button>
                    </td>
                    <td className="p-4 bg-primary/5">
                      <Button 
                        className="w-full bg-accent hover:bg-accent/90"
                        onClick={() => handleSelectPlan('PRO')}
                        disabled={loadingPlan === 'PRO'}
                      >
                        {loadingPlan === 'PRO' ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          'Get Started'
                        )}
                      </Button>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Upgrade Confirmation Text */}
        <div className="mt-8 p-4 bg-muted/30 rounded-lg border border-border">
          <p className="text-sm text-muted-foreground text-center">
            By upgrading, you agree to the billing terms and understand that your subscription will renew automatically each month unless cancelled. All use of the platform must follow our{' '}
            <a href="/legal/terms-of-service" className="text-primary hover:underline">Terms of Service</a>
            {', '}
            <a href="/legal/privacy-policy" className="text-primary hover:underline">Privacy Policy</a>
            {', and '}
            <a href="/legal/acceptable-use" className="text-primary hover:underline">Acceptable Use Policy</a>
            .
          </p>
        </div>

        {/* FAQ or additional info */}
        <div className="mt-8 text-center">
          <p className="text-muted-foreground text-sm">
            All plans include a 30-day money-back guarantee. Cancel anytime.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}
