import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { authService } from '@/lib/api/auth';
import { useToast } from '@/hooks/use-toast';

export default function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    const access = searchParams.get('access');
    const refresh = searchParams.get('refresh');
    const error = searchParams.get('error');

    if (error) {
      // Handle error
      let errorMessage = 'Google sign-in failed. Please try again.';
      
      if (error === 'invalid_state') {
        errorMessage = 'Security validation failed. Please try signing in again.';
      } else if (error === 'no_code') {
        errorMessage = 'Authorization failed. Please try signing in again.';
      } else if (error === 'oauth_failed') {
        errorMessage = 'Google authentication failed. Please try again.';
      }
      
      toast({
        title: 'Sign-in failed',
        description: errorMessage,
        variant: 'destructive',
      });
      
      navigate('/');
      return;
    }

    if (access && refresh) {
      // Store tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      // Fetch user data and update auth context
      authService.getCurrentUser()
        .then((user) => {
          refreshUser();
          toast({
            title: 'Welcome!',
            description: `Successfully signed in as ${user.email}`,
          });
          navigate('/');
        })
        .catch((err) => {
          toast({
            title: 'Sign-in incomplete',
            description: 'Signed in with Google, but failed to load your profile. Please refresh the page.',
            variant: 'destructive',
          });
          navigate('/');
        });
    } else {
      toast({
        title: 'Sign-in failed',
        description: 'No authentication tokens received. Please try again.',
        variant: 'destructive',
      });
      navigate('/');
    }
  }, [searchParams, navigate, refreshUser, toast]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center space-y-4">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <h2 className="text-xl font-semibold text-foreground">Completing sign in...</h2>
        <p className="text-muted-foreground">Please wait while we sign you in with Google.</p>
      </div>
    </div>
  );
}

