import { useState, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { Loader2, X, Mail, Lock, User, ArrowRight, ArrowLeft, Eye, EyeOff, CheckCircle2, AlertCircle } from 'lucide-react';
import { z } from 'zod';
import logo from '@/assets/logo.png';

const emailSchema = z.string().email('Please enter a valid email address');
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number');

/**
 * Calculates password strength based on various criteria.
 * Returns a value between 0 and 100.
 */
const calculatePasswordStrength = (password: string): number => {
  if (!password) return 0;

  let strength = 0;

  // Length check (max 40 points)
  if (password.length >= 8) strength += 20;
  if (password.length >= 12) strength += 20;

  // Character variety checks (max 60 points)
  if (/[a-z]/.test(password)) strength += 15;
  if (/[A-Z]/.test(password)) strength += 15;
  if (/[0-9]/.test(password)) strength += 15;
  if (/[^a-zA-Z0-9]/.test(password)) strength += 15;

  return Math.min(strength, 100);
};

/**
 * Gets password strength label and color.
 */
const getPasswordStrengthInfo = (strength: number): { label: string; color: string } => {
  if (strength < 30) return { label: 'Weak', color: 'bg-destructive' };
  if (strength < 60) return { label: 'Fair', color: 'bg-orange-500' };
  if (strength < 80) return { label: 'Good', color: 'bg-yellow-500' };
  return { label: 'Strong', color: 'bg-green-500' };
};

interface AuthModalProps {
  onClose?: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; firstName?: string; lastName?: string; terms?: string }>({});
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmailSent, setResetEmailSent] = useState(false);
  const { signIn, signUp } = useAuth();
  const { toast } = useToast();

  // Calculate password strength in real-time
  const passwordStrength = useMemo(() => calculatePasswordStrength(password), [password]);
  const passwordStrengthInfo = useMemo(() => getPasswordStrengthInfo(passwordStrength), [passwordStrength]);

  // Password requirements checklist
  const passwordRequirements = useMemo(() => {
    return [
      { label: 'At least 8 characters', met: password.length >= 8 },
      { label: 'One uppercase letter', met: /[A-Z]/.test(password) },
      { label: 'One lowercase letter', met: /[a-z]/.test(password) },
      { label: 'One number', met: /[0-9]/.test(password) },
    ];
  }, [password]);

  /**
   * Validates the signup form with comprehensive checks.
   * Returns true if all validations pass.
   */
  const validateSignupForm = () => {
    const newErrors: { email?: string; password?: string; firstName?: string; lastName?: string; terms?: string } = {};

    // Validate first name
    if (!firstName.trim()) {
      newErrors.firstName = 'First name is required';
    } else if (firstName.trim().length < 2) {
      newErrors.firstName = 'First name must be at least 2 characters';
    }

    // Validate last name
    if (!lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    } else if (lastName.trim().length < 2) {
      newErrors.lastName = 'Last name must be at least 2 characters';
    }

    // Validate email
    const emailResult = emailSchema.safeParse(email);
    if (!emailResult.success) {
      newErrors.email = emailResult.error.errors[0].message;
    }

    // Validate password
    const passwordResult = passwordSchema.safeParse(password);
    if (!passwordResult.success) {
      newErrors.password = passwordResult.error.errors[0].message;
    }

    // Validate terms acceptance
    if (!acceptedTerms) {
      newErrors.terms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Validates the signin form.
   */
  const validateSigninForm = () => {
    const newErrors: { email?: string; password?: string } = {};

    const emailResult = emailSchema.safeParse(email);
    if (!emailResult.success) {
      newErrors.email = emailResult.error.errors[0].message;
    }

    if (!password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateSigninForm()) return;

    setIsLoading(true);
    const { error } = await signIn(email, password);
    setIsLoading(false);

    if (error) {
      let message = 'Invalid email or password';

      if (typeof error === 'string') {
        message = error;
      } else if (error && typeof error === 'object') {
        // Check for backend error format: { error: "message", detail: "..." }
        if (error.error) {
          message = error.error;
        } else if (error.message) {
          message = error.message;
        } else if (error.non_field_errors && Array.isArray(error.non_field_errors)) {
          message = error.non_field_errors[0] || message;
        }
      }

      toast({
        title: 'Sign in failed',
        description: message,
        variant: 'destructive',
      });
    } else {
      if (onClose) onClose();
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateSignupForm()) return;

    setIsLoading(true);
    setErrors({}); // Clear previous errors

    const { error, message: successMessage } = await signUp(email, password, firstName, lastName);
    setIsLoading(false);

    if (!error) {
      // Registration successful - show success message
      toast({
        title: 'Account created successfully!',
        description: successMessage || 'Please check your email to verify your account before signing in.',
        variant: 'default',
      });

      // Clear form and switch to sign in tab
      setEmail('');
      setPassword('');
      setFirstName('');
      setLastName('');
      setActiveTab('signin');
      return;
    }

    if (error) {
      // Extract field-specific errors
      const fieldErrors: { email?: string; password?: string; first_name?: string; last_name?: string; firstName?: string; lastName?: string } = {};

      // Handle different error response formats
      if (typeof error === 'object' && error !== null) {
        // Check for errors object (from backend validation) - this is the primary format
        if (error.errors && typeof error.errors === 'object') {
          // Map backend field names to frontend field names
          if (error.errors.email) {
            fieldErrors.email = typeof error.errors.email === 'string'
              ? error.errors.email
              : Array.isArray(error.errors.email)
                ? error.errors.email[0]
                : 'Invalid email';
          }
          if (error.errors.first_name) {
            fieldErrors.firstName = typeof error.errors.first_name === 'string'
              ? error.errors.first_name
              : Array.isArray(error.errors.first_name)
                ? error.errors.first_name[0]
                : 'Invalid first name';
          }
          if (error.errors.last_name) {
            fieldErrors.lastName = typeof error.errors.last_name === 'string'
              ? error.errors.last_name
              : Array.isArray(error.errors.last_name)
                ? error.errors.last_name[0]
                : 'Invalid last name';
          }
          if (error.errors.password) {
            fieldErrors.password = typeof error.errors.password === 'string'
              ? error.errors.password
              : Array.isArray(error.errors.password)
                ? error.errors.password[0]
                : 'Invalid password';
          }
        }

        // Also check for direct field errors (legacy format or alternative structure)
        if (error.email && !fieldErrors.email) {
          fieldErrors.email = Array.isArray(error.email) ? error.email[0] : String(error.email);
        }
        if ((error.first_name || error.firstName) && !fieldErrors.firstName) {
          const firstNameError = error.first_name || error.firstName;
          fieldErrors.firstName = Array.isArray(firstNameError)
            ? firstNameError[0]
            : String(firstNameError);
        }
        if ((error.last_name || error.lastName) && !fieldErrors.lastName) {
          const lastNameError = error.last_name || error.lastName;
          fieldErrors.lastName = Array.isArray(lastNameError)
            ? lastNameError[0]
            : String(lastNameError);
        }
        if (error.password && !fieldErrors.password) {
          fieldErrors.password = Array.isArray(error.password) ? error.password[0] : String(error.password);
        }
      }

      // Set field-specific errors - always set even if empty to clear previous errors
      setErrors(fieldErrors);

      // Get primary error message for toast
      let errorMessage = typeof error === 'string'
        ? error
        : error.error || error.message || 'Registration failed';

      // Improve user-friendly messages
      if (fieldErrors.email) {
        errorMessage = fieldErrors.email;
        if (errorMessage.toLowerCase().includes('already exists') ||
          errorMessage.toLowerCase().includes('already registered') ||
          errorMessage.toLowerCase().includes('user with this email')) {
          errorMessage = 'This email is already registered. Please sign in instead.';
          fieldErrors.email = 'This email is already registered. Please sign in instead.';
          // Update errors state with improved message
          setErrors(fieldErrors);
        }
      } else if (fieldErrors.firstName) {
        errorMessage = fieldErrors.firstName;
      } else if (fieldErrors.lastName) {
        errorMessage = fieldErrors.lastName;
      } else if (fieldErrors.password) {
        errorMessage = fieldErrors.password;
      }

      toast({
        title: 'Sign up failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } else {
      toast({
        title: 'Account created!',
        description: 'Please check your email to verify your account.',
      });
      if (onClose) onClose();
    }
  };

  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    setIsGoogleLoading(true);
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const cleanBaseUrl = apiBaseUrl.replace(/\/+$/, '');
      const healthUrl = `${cleanBaseUrl}/api/health/`;
      const googleAuthUrl = `${cleanBaseUrl}/api/accounts/google/login/`.replace(/([^:]\/)\/+/g, '$1');

      // Ping the backend first to wake it up (Render free plan spins down)
      // Retry up to 6 times (total ~90 seconds for cold start)
      let backendReady = false;
      for (let attempt = 0; attempt < 6; attempt++) {
        try {
          const res = await fetch(healthUrl, { method: 'GET', mode: 'cors', signal: AbortSignal.timeout(15000) });
          if (res.ok) {
            backendReady = true;
            break;
          }
        } catch {
          // Backend still waking up, wait and retry
          await new Promise(r => setTimeout(r, 3000));
        }
      }

      if (!backendReady) {
        toast({
          title: 'Server is starting up',
          description: 'Please wait a moment and try again.',
          variant: 'destructive',
        });
        setIsLoading(false);
        setIsGoogleLoading(false);
        return;
      }

      window.location.href = googleAuthUrl;
    } catch {
      toast({
        title: 'Sign in failed',
        description: 'Google sign in is not available yet. Please use email and password.',
        variant: 'destructive',
      });
      setIsLoading(false);
      setIsGoogleLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    const emailResult = emailSchema.safeParse(email);
    if (!emailResult.success) {
      setErrors({ email: emailResult.error.errors[0].message });
      return;
    }

    setIsLoading(true);
    try {
      // Import authService for password reset
      const { authService } = await import('@/lib/api');
      await authService.requestPasswordReset(email);
      toast({
        title: 'Reset email sent',
        description: 'Please check your email for password reset instructions.',
      });
      setResetEmailSent(true);
    } catch (error) {
      const message = error instanceof Error && 'response' in error
        ? (error as { response?: { data?: { message?: string } } }).response?.data?.message
        : undefined;
      toast({
        title: 'Reset failed',
        description: message || 'Failed to send reset email. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Forgot Password View
  if (showForgotPassword) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background/95 to-accent/5 backdrop-blur-md" />

        <Card className="relative w-full max-w-lg shadow-2xl border-0 bg-card/95 backdrop-blur-xl animate-fade-in overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-accent to-primary" />

          <CardHeader className="text-center pb-2 pt-8">
            <div className="mx-auto mb-4 p-3 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 border border-border/50">
              <img src={logo} alt="Food Science Toolbox" className="h-10" />
            </div>
            <CardTitle className="text-2xl font-bold">
              {resetEmailSent ? 'Check Your Email' : 'Reset Password'}
            </CardTitle>
            <CardDescription className="text-base">
              {resetEmailSent
                ? 'We sent a password reset link to your email'
                : 'Enter your email to receive a reset link'
              }
            </CardDescription>
          </CardHeader>

          <CardContent className="px-6 pb-6">
            {resetEmailSent ? (
              <div className="space-y-4">
                <div className="bg-accent/10 rounded-lg p-4 text-center">
                  <Mail className="h-12 w-12 mx-auto mb-3 text-primary" />
                  <p className="text-sm text-muted-foreground">
                    Click the link in your email to reset your password. If you don't see it, check your spam folder.
                  </p>
                </div>
                <Button
                  variant="outline"
                  className="w-full h-11"
                  onClick={() => {
                    setShowForgotPassword(false);
                    setResetEmailSent(false);
                    setEmail('');
                  }}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Sign In
                </Button>
              </div>
            ) : (
              <form onSubmit={handleForgotPassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="reset-email" className="text-sm font-medium">
                    Email Address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="reset-email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className={`pl-10 h-11 bg-muted/30 border-muted-foreground/20 focus:border-primary transition-colors ${errors.email ? 'border-destructive' : ''}`}
                    />
                  </div>
                  {errors.email && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="inline-block w-1 h-1 rounded-full bg-destructive" />
                      {errors.email}
                    </p>
                  )}
                </div>
                <Button
                  type="submit"
                  className="w-full h-11 font-medium bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary shadow-lg shadow-primary/25 transition-all"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      Send Reset Link
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full h-11"
                  onClick={() => {
                    setShowForgotPassword(false);
                    setErrors({});
                  }}
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Sign In
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop with gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background/95 to-accent/5 backdrop-blur-md" />

      {/* Modal */}
      <Card className="relative w-full max-w-lg shadow-2xl border-0 bg-card/95 backdrop-blur-xl animate-fade-in overflow-hidden">
        {/* Decorative gradient bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-accent to-primary" />

        {onClose && (
          <button
            onClick={onClose}
            className="absolute right-4 top-4 p-1.5 rounded-full bg-muted/50 opacity-70 ring-offset-background transition-all hover:opacity-100 hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </button>
        )}

        <CardHeader className="text-center pb-2 pt-8">
          <div className="mx-auto mb-4 p-3 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 border border-border/50">
            <img src={logo} alt="Food Science Toolbox" className="h-10" />
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
            Welcome to Food Science Toolbox
          </CardTitle>
          <CardDescription className="text-base">
            Sign in to your account or create a new one
          </CardDescription>
        </CardHeader>

        <CardContent className="px-6 pb-6">
          <Tabs defaultValue="signin" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6 p-1 bg-muted/50">
              <TabsTrigger
                value="signin"
                className="data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all"
              >
                Sign In
              </TabsTrigger>
              <TabsTrigger
                value="signup"
                className="data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all"
              >
                Sign Up
              </TabsTrigger>
            </TabsList>

            <TabsContent value="signin" className="mt-0">
              <form onSubmit={handleSignIn} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signin-email" className="text-sm font-medium">
                    Email Address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signin-email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className={`pl-10 h-11 bg-muted/30 border-muted-foreground/20 focus:border-primary transition-colors ${errors.email ? 'border-destructive' : ''}`}
                    />
                  </div>
                  {errors.email && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="inline-block w-1 h-1 rounded-full bg-destructive" />
                      {errors.email}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signin-password" className="text-sm font-medium">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signin-password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className={`pl-10 h-11 bg-muted/30 border-muted-foreground/20 focus:border-primary transition-colors ${errors.password ? 'border-destructive' : ''}`}
                    />
                  </div>
                  {errors.password && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="inline-block w-1 h-1 rounded-full bg-destructive" />
                      {errors.password}
                    </p>
                  )}
                </div>
                <Button
                  type="submit"
                  className="w-full h-11 font-medium bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary shadow-lg shadow-primary/25 transition-all"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    <>
                      Sign In
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="w-full text-sm text-primary hover:text-primary/80 hover:underline transition-colors"
                >
                  Forgot your password?
                </button>
              </form>
            </TabsContent>

            <TabsContent value="signup" className="mt-0">
              <form onSubmit={handleSignUp} className="space-y-3">
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-firstname" className="text-sm font-semibold">
                      First Name
                    </Label>
                    <div className="relative group">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                      <Input
                        id="signup-firstname"
                        type="text"
                        placeholder="John"
                        value={firstName}
                        onChange={(e) => {
                          setFirstName(e.target.value);
                          if (errors.firstName) {
                            setErrors(prev => ({ ...prev, firstName: undefined }));
                          }
                        }}
                        className={`pl-10 h-11 bg-background/50 border-2 transition-all duration-200 ${errors.firstName
                            ? 'border-destructive focus-visible:border-destructive'
                            : 'border-border focus-visible:border-primary'
                          } ${firstName && !errors.firstName ? 'border-green-500/50' : ''}`}
                      />
                    </div>
                    {errors.firstName && (
                      <p className="text-xs text-destructive flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.firstName}
                      </p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-lastname" className="text-sm font-semibold">
                      Last Name
                    </Label>
                    <div className="relative group">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                      <Input
                        id="signup-lastname"
                        type="text"
                        placeholder="Doe"
                        value={lastName}
                        onChange={(e) => {
                          setLastName(e.target.value);
                          if (errors.lastName) {
                            setErrors(prev => ({ ...prev, lastName: undefined }));
                          }
                        }}
                        className={`pl-10 h-11 bg-background/50 border-2 transition-all duration-200 ${errors.lastName
                            ? 'border-destructive focus-visible:border-destructive'
                            : 'border-border focus-visible:border-primary'
                          } ${lastName && !errors.lastName ? 'border-green-500/50' : ''}`}
                      />
                    </div>
                    {errors.lastName && (
                      <p className="text-xs text-destructive flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1">
                        <AlertCircle className="h-3 w-3" />
                        {errors.lastName}
                      </p>
                    )}
                  </div>
                </div>

                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="signup-email" className="text-sm font-semibold">
                    Email Address
                  </Label>
                  <div className="relative group">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="john.doe@example.com"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (errors.email) {
                          setErrors(prev => ({ ...prev, email: undefined }));
                        }
                      }}
                      className={`pl-10 h-11 bg-background/50 border-2 transition-all duration-200 ${errors.email
                          ? 'border-destructive focus-visible:border-destructive'
                          : 'border-border focus-visible:border-primary'
                        } ${email && !errors.email && emailSchema.safeParse(email).success ? 'border-green-500/50' : ''}`}
                    />
                  </div>
                  {errors.email && (
                    <p className="text-xs text-destructive flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Password Field with Strength Indicator */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="signup-password" className="text-sm font-semibold">
                      Password
                    </Label>
                    {password && (
                      <div className="flex items-center gap-1.5">
                        <div className={`h-1.5 w-12 rounded-full ${passwordStrengthInfo.color} transition-all duration-300`} />
                        <span className="text-xs text-muted-foreground">
                          {passwordStrengthInfo.label}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="relative group">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
                    <Input
                      id="signup-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a strong password"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        if (errors.password) {
                          setErrors(prev => ({ ...prev, password: undefined }));
                        }
                      }}
                      className={`pl-10 pr-10 h-11 bg-background/50 border-2 transition-all duration-200 ${errors.password
                          ? 'border-destructive focus-visible:border-destructive'
                          : 'border-border focus-visible:border-primary'
                        } ${password && !errors.password && passwordSchema.safeParse(password).success ? 'border-green-500/50' : ''}`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      tabIndex={-1}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>

                  {/* Password Requirements - Compact Inline */}
                  {password && (
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs animate-in fade-in slide-in-from-top-1">
                      {passwordRequirements.map((req, index) => (
                        <div key={index} className="flex items-center gap-1.5">
                          {req.met ? (
                            <CheckCircle2 className="h-3 w-3 text-green-500 flex-shrink-0" />
                          ) : (
                            <div className="h-3 w-3 rounded-full border border-muted-foreground/30 flex-shrink-0" />
                          )}
                          <span className={req.met ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}>
                            {req.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  {errors.password && (
                    <p className="text-xs text-destructive flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors.password}
                    </p>
                  )}
                </div>

                {/* Terms and Conditions */}
                <div className="space-y-1.5">
                  <div className="flex items-start gap-2.5 py-2">
                    <Checkbox
                      id="terms"
                      checked={acceptedTerms}
                      onCheckedChange={(checked) => {
                        setAcceptedTerms(checked === true);
                        if (errors.terms) {
                          setErrors(prev => ({ ...prev, terms: undefined }));
                        }
                      }}
                      className="mt-0.5"
                    />
                    <Label
                      htmlFor="terms"
                      className="text-xs leading-relaxed cursor-pointer flex-1"
                    >
                      I have read and agree to the{' '}
                      <a href="/legal/terms-of-service" target="_blank" className="text-primary hover:underline">
                        Terms of Service
                      </a>
                      {', '}
                      <a href="/legal/privacy-policy" target="_blank" className="text-primary hover:underline">
                        Privacy Policy
                      </a>
                      {', and '}
                      <a href="/legal/acceptable-use" target="_blank" className="text-primary hover:underline">
                        Acceptable Use Policy
                      </a>
                      .
                    </Label>
                  </div>
                  {errors.terms && (
                    <p className="text-xs text-destructive flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1 ml-7">
                      <AlertCircle className="h-3 w-3" />
                      {errors.terms}
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full h-11 font-semibold bg-gradient-to-r from-primary via-primary to-primary/90 hover:from-primary/90 hover:via-primary hover:to-primary shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={isLoading || !acceptedTerms}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating account...
                    </>
                  ) : (
                    <>
                      Create Account
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>

                {/* Free Trial Banner - Compact */}
                <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg p-2.5 border border-primary/20">
                  <p className="text-xs text-center text-muted-foreground">
                    <span className="font-semibold text-foreground">Free 7-day trial</span> • 10 free generations • No credit card required
                  </p>
                </div>
              </form>
            </TabsContent>
          </Tabs>

          {/* Divider */}
          <div className="relative my-6">
            <Separator className="bg-border/50" />
            <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-3 text-xs text-muted-foreground font-medium">
              or continue with
            </span>
          </div>

          {/* Google Sign In Button */}
          <Button
            variant="outline"
            className="w-full h-11 bg-muted/30 border-muted-foreground/20 hover:bg-muted hover:border-muted-foreground/40 transition-all"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
          >
            {isGoogleLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connecting to server...
              </>
            ) : (
              <>
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Continue with Google
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
