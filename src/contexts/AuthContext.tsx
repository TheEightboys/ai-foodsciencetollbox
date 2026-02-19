import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService, User } from '@/lib/api/auth';
import {
  supabaseSignIn,
  supabaseSignUp,
  supabaseSignOut,
  restoreSupabaseSession,
} from '@/lib/api/supabaseAuth';

interface AuthError {
  message?: string;
  email?: string[];
  password?: string[];
  [key: string]: unknown;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signUp: (email: string, password: string, firstName: string, lastName: string) => Promise<{ error: AuthError | null }>;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      // Try to restore a Supabase session first (covers page reload / returning users)
      try {
        const djangoAuth = await restoreSupabaseSession();
        if (djangoAuth) {
          setUser(djangoAuth.user as User);
          setLoading(false);
          return;
        }
      } catch {
        // Supabase session not available, fall through to token check
      }

      // Fallback: check existing Django JWT stored in localStorage
      const token = authService.getAccessToken();
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const signUp = async (email: string, password: string, firstName: string, lastName: string) => {
    try {
      const result = await supabaseSignUp(email, password, firstName, lastName);
      if (result.user) {
        setUser(result.user as User);
      }
      return { error: null, message: result.message };
    } catch (error) {
      const err = error as Error;
      return { error: { message: err.message || 'Registration failed. Please try again.' } };
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const response = await supabaseSignIn(email, password);
      setUser(response.user as User);
      return { error: null };
    } catch (error) {
      const err = error as Error;
      return { error: { message: err.message || 'Login failed. Please check your credentials and try again.' } };
    }
  };

  const signOut = async () => {
    setUser(null);
    try {
      await supabaseSignOut();
    } catch {
      // Ignore errors — tokens cleared locally
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        signUp,
        signIn,
        signOut,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
