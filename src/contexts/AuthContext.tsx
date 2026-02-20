import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  ReactNode,
} from "react";
import { authService, User } from "@/lib/api/auth";
import { supabase } from "@/lib/supabase";
import {
  supabaseSignIn,
  supabaseSignUp,
  supabaseSignOut,
  restoreSupabaseSession,
} from "@/lib/api/supabaseAuth";

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
  signUp: (
    email: string,
    password: string,
    firstName: string,
    lastName: string,
  ) => Promise<{ error: AuthError | null }>;
  signIn: (
    email: string,
    password: string,
  ) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  // Guard: tracks whether a sign-in is in progress so that the
  // onAuthStateChange listener does not interfere (e.g. a spurious
  // SIGNED_OUT event or duplicate token exchange).
  const signingInRef = useRef(false);

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
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    checkAuth();

    // Listen for Supabase auth events (e.g. Google OAuth callback, token refresh)
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      // Skip listener processing while a direct signIn/signUp call is
      // in-flight — the signIn function handles setUser itself and the
      // listener would otherwise cause a race condition or duplicate
      // token exchange that can momentarily clear the user.
      if (signingInRef.current) return;

      if ((event === "SIGNED_IN" || event === "TOKEN_REFRESHED") && session) {
        try {
          const djangoAuth = await restoreSupabaseSession();
          if (djangoAuth) {
            setUser(djangoAuth.user as User);
            setLoading(false);
          }
        } catch {
          // Fallback: build user from Supabase session metadata
          const meta = session.user?.user_metadata || {};
          const fullName: string = meta.full_name || "";
          const parts = fullName.trim().split(/\s+/);
          setUser({
            id: 0,
            email: session.user?.email || "",
            first_name: meta.first_name || meta.given_name || parts[0] || "",
            last_name:
              meta.last_name ||
              meta.family_name ||
              parts.slice(1).join(" ") ||
              "",
          } as User);
          setLoading(false);
        }
      } else if (event === "SIGNED_OUT") {
        setUser(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (
    email: string,
    password: string,
    firstName: string,
    lastName: string,
  ) => {
    try {
      const result = await supabaseSignUp(email, password, firstName, lastName);
      if (result.user) {
        setUser(result.user as User);
      }
      return { error: null, message: result.message };
    } catch (error) {
      const err = error as Error;
      return {
        error: {
          message: err.message || "Registration failed. Please try again.",
        },
      };
    }
  };

  const signIn = async (email: string, password: string) => {
    signingInRef.current = true;
    try {
      const response = await supabaseSignIn(email, password);
      setUser(response.user as User);
      setLoading(false);
      return { error: null };
    } catch (error) {
      const err = error as Error;
      return {
        error: {
          message:
            err.message ||
            "Login failed. Please check your credentials and try again.",
        },
      };
    } finally {
      signingInRef.current = false;
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
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
