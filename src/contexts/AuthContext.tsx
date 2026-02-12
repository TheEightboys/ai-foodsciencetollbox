import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService, User } from '@/lib/api/auth';

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
      const token = authService.getAccessToken();
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Token invalid or expired - clear it
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
      const response = await authService.register({
        email,
        password,
        password_confirm: password,
        first_name: firstName,
        last_name: lastName,
      });
      return { error: null, message: response.message || 'Registration successful! Please check your email to verify your account.' };
    } catch (error) {
      const axiosError = error as { 
        response?: { data?: AuthError }; 
        message?: string;
        code?: string;
      };
      
      // Network error - backend not reachable
      if (!axiosError.response) {
        const isProduction = !import.meta.env.DEV;
        
        let errorMessage: string;
        if (axiosError.code === 'ECONNABORTED') {
          errorMessage = 'Request timed out. Please try again or contact support if the problem persists.';
        } else if (axiosError.message?.includes('Network Error') || axiosError.code === 'ERR_NETWORK') {
          errorMessage = isProduction
            ? 'Cannot connect to backend API. Please check your network connection or contact support.'
            : 'Cannot connect to server. Please ensure the backend is running.';
        } else {
          errorMessage = isProduction
            ? 'Unable to connect to server. Please check your network connection or contact support.'
            : 'Unable to connect to server. Please check your connection and ensure the backend is running.';
        }
        
        return { 
          error: { 
            message: errorMessage 
          } 
        };
      }
      
      return { 
        error: axiosError.response?.data || { message: 'Registration failed. Please try again.' } 
      };
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const response = await authService.login({ email, password });
      setUser(response.user);
      return { error: null };
    } catch (error) {
      const axiosError = error as { response?: { data?: AuthError & { error?: string; detail?: string } } };
      const errorData = axiosError.response?.data;
      
      // Extract error message from backend response
      // Backend returns { error: "...", detail: "..." } format
      if (errorData) {
        if (errorData.error) {
          // Backend error format: { error: "message", detail: "..." }
          return { error: { message: errorData.error } };
        } else if (errorData.message) {
          // Standard format: { message: "..." }
          return { error: { message: errorData.message } };
        } else if (errorData.non_field_errors) {
          // DRF format: { non_field_errors: [...] }
          return { error: { message: errorData.non_field_errors[0] } };
        }
      }
      
      return { error: { message: 'Login failed. Please check your credentials and try again.' } };
    }
  };

  const signOut = async () => {
    // Clear user state immediately for better UX
    setUser(null);
    
    // Logout from backend (non-blocking)
    try {
      await authService.logout();
    } catch (error) {
      // Ignore errors - user is already signed out locally
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
