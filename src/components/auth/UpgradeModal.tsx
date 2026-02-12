import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MEMBERSHIP_TIERS } from '@/lib/constants';
import { Check, Sparkles, Crown, Zap, Star, X, Rocket } from 'lucide-react';

interface UpgradeModalProps {
  onClose: () => void;
}

export function UpgradeModal({ onClose }: UpgradeModalProps) {
  const navigate = useNavigate();

  const tierIcons = {
    TRIAL: <Sparkles className="h-5 w-5" />,
    STARTER: <Zap className="h-5 w-5" />,
    PRO: <Star className="h-5 w-5" />,
  };

  const handleSelectPlan = (tierKey: string) => {
    if (tierKey === 'TRIAL') {
      onClose();
    } else {
      navigate(`/pricing?plan=${tierKey.toLowerCase()}`);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <Card className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl border-border/50 animate-fade-in">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 z-10 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          <X className="h-5 w-5" />
          <span className="sr-only">Close</span>
        </button>
        
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4 p-3 rounded-full bg-primary/10">
            <Rocket className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">Welcome to Food Science Toolbox!</CardTitle>
          <CardDescription className="text-base">
            Choose a plan to unlock the full potential of our AI-powered lesson generators
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(MEMBERSHIP_TIERS)
              .map(([key, tier]) => {
                const tierKey = key as keyof typeof tierIcons;
                const isPopular = key === 'PRO';
                const isTrial = key === 'TRIAL';
                
                return (
                  <Card 
                    key={key} 
                    className={`relative transition-all hover:shadow-lg ${
                      isPopular ? 'ring-2 ring-accent border-accent' : 'border-border'
                    }`}
                  >
                    {isPopular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="bg-accent text-accent-foreground text-xs font-semibold px-3 py-1 rounded-full">
                          Recommended
                        </span>
                      </div>
                    )}
                    
                    <CardHeader className="text-center pb-2 pt-6">
                      <div className={`mx-auto mb-2 p-2 rounded-full bg-muted`}>
                        {tierIcons[tierKey]}
                      </div>
                      <CardTitle className="text-lg">{tier.name}</CardTitle>
                      <div className="mt-2">
                        {'monthly' in tier.price ? (
                          <>
                            <span className="text-2xl font-bold text-foreground">
                              ${tier.price.monthly}
                            </span>
                            <span className="text-muted-foreground">/mo</span>
                          </>
                        ) : (
                          <>
                            <span className="text-2xl font-bold text-foreground">
                              ${tier.price.oneTime}
                            </span>
                            <span className="text-muted-foreground"> one-time</span>
                          </>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {tier.generations === -1 ? 'Unlimited' : tier.generations} generations/month
                      </p>
                    </CardHeader>
                    
                    <CardContent className="pt-0">
                      <ul className="space-y-1.5 text-sm mb-4">
                        {tier.features.slice(0, 3).map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <Check className="h-4 w-4 text-accent shrink-0 mt-0.5" />
                            <span className="text-muted-foreground text-xs">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <Button 
                        className={`w-full ${isPopular ? 'bg-accent hover:bg-accent/90' : ''}`}
                        variant={isTrial ? 'outline' : 'default'}
                        onClick={() => handleSelectPlan(key)}
                      >
                        {isTrial ? 'Continue with Trial' : 'Select Plan'}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
          </div>
          
          <p className="text-center text-sm text-muted-foreground mt-6">
            You can always upgrade or change your plan later from your dashboard.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
