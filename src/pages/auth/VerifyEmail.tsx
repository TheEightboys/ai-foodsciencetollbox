import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle2, XCircle, Mail } from 'lucide-react';
import apiClient from '@/lib/api/client';
import { useToast } from '@/hooks/use-toast';

export default function VerifyEmail() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. Please check your email and try again.');
        return;
      }

      try {
        const response = await apiClient.get(`/accounts/verify-email/${token}/`);
        
        if (response.data.verified || response.data.message) {
          setStatus('success');
          setMessage(response.data.message || 'Email verified successfully!');
          
          // Show success toast
          toast({
            title: 'Email verified!',
            description: 'Your email has been verified. You can now sign in.',
          });
          
          // Redirect to home page (which will show sign in) after 2 seconds
          setTimeout(() => {
            navigate('/', { replace: true });
          }, 2000);
        } else {
          setStatus('error');
          setMessage(response.data.error || 'Verification failed. Please try again.');
        }
      } catch (error: any) {
        setStatus('error');
        const errorMessage = error?.response?.data?.error || 
                           error?.response?.data?.detail || 
                           'Verification failed. Please try again or request a new verification email.';
        setMessage(errorMessage);
      }
    };

    verifyEmail();
  }, [token, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {status === 'loading' && <Loader2 className="h-12 w-12 animate-spin text-primary" />}
            {status === 'success' && <CheckCircle2 className="h-12 w-12 text-green-500" />}
            {status === 'error' && <XCircle className="h-12 w-12 text-destructive" />}
          </div>
          <CardTitle className="text-2xl">
            {status === 'loading' && 'Verifying Email...'}
            {status === 'success' && 'Email Verified!'}
            {status === 'error' && 'Verification Failed'}
          </CardTitle>
          <CardDescription>
            {status === 'loading' && 'Please wait while we verify your email address.'}
            {status === 'success' && 'Your email has been successfully verified.'}
            {status === 'error' && 'We could not verify your email address.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-center text-muted-foreground">{message}</p>
          
          {status === 'success' && (
            <div className="text-center text-sm text-muted-foreground">
              <p>Redirecting you to sign in...</p>
            </div>
          )}
          
          {status === 'error' && (
            <div className="space-y-2">
              <Button 
                className="w-full" 
                onClick={() => navigate('/?verified=0', { replace: true })}
              >
                Go to Sign In
              </Button>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => navigate('/pricing')}
              >
                Sign Up Again
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

