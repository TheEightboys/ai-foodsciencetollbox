import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { AuthModal } from './AuthModal';
import { UpgradeModal } from './UpgradeModal';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { authService } from '@/lib/api/auth';
import { Loader2, Mail } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const { toast } = useToast();
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [hasShownUpgrade, setHasShownUpgrade] = useState(false);
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    // Check if user just signed up (new user) and hasn't seen upgrade modal
    if (user && !hasShownUpgrade) {
      const hasSeenUpgrade = localStorage.getItem(`upgrade_shown_${user.id}`);
      if (!hasSeenUpgrade) {
        // Small delay to let the auth modal close first
        const timer = setTimeout(() => {
          setShowUpgradeModal(true);
          setHasShownUpgrade(true);
          localStorage.setItem(`upgrade_shown_${user.id}`, 'true');
        }, 500);
        return () => clearTimeout(timer);
      }
    }
  }, [user, hasShownUpgrade]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Show blurred dashboard with auth modal if not logged in
  if (!user) {
    return (
      <div className="relative">
        {/* Blurred content */}
        <div className="blur-md pointer-events-none select-none" aria-hidden="true">
          {children}
        </div>
        
        {/* Auth modal overlay */}
        <AuthModal />
      </div>
    );
  }

  // Check if email is verified - if not, show verification message
  if (user && user.email_verified === false) {
    const handleResendVerification = async () => {
      setIsResending(true);
      try {
        await authService.resendVerificationEmail();
        toast({
          title: 'Verification email sent',
          description: 'Please check your email for the verification link.',
        });
      } catch (error: any) {
        const message = error?.response?.data?.error || error?.response?.data?.message || 'Failed to send verification email. Please try again.';
        toast({
          title: 'Failed to send email',
          description: message,
          variant: 'destructive',
        });
      } finally {
        setIsResending(false);
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="max-w-md w-full space-y-4 text-center">
          <h1 className="text-2xl font-bold">Please Verify Your Email</h1>
          <p className="text-muted-foreground">
            We've sent a verification link to <strong>{user.email}</strong>. 
            Please check your email and click the verification link to activate your account.
          </p>
          <p className="text-sm text-muted-foreground">
            If you didn't receive the email, please check your spam folder or contact support.
          </p>
          <Button
            onClick={handleResendVerification}
            disabled={isResending}
            className="w-full"
            variant="outline"
          >
            {isResending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Mail className="h-4 w-4 mr-2" />
                Resend Verification Email
              </>
            )}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      {children}
      
      {/* Upgrade modal shown after signup */}
      {showUpgradeModal && (
        <UpgradeModal onClose={() => setShowUpgradeModal(false)} />
      )}
    </>
  );
}
