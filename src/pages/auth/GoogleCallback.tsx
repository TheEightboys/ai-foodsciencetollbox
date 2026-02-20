import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import {
  exchangeSupabaseTokenForDjango,
  exchangeGoogleCode,
} from "@/lib/api/supabaseAuth";
import { useToast } from "@/hooks/use-toast";

export default function GoogleCallback() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const error = params.get("error");

    // ── Direct Google OAuth flow (VITE_GOOGLE_CLIENT_ID is set) ──────────────
    // Google redirected here with ?code=... — exchange it via the Django backend.
    if (code) {
      exchangeGoogleCode(code)
        .then((auth) => {
          toast({
            title: "Welcome!",
            description: `Signed in as ${auth.user.email}`,
          });
          navigate("/dashboard");
        })
        .catch((err: unknown) => {
          const message =
            err instanceof Error ? err.message : "Google sign-in failed.";
          toast({
            title: "Google sign-in failed",
            description: message,
            variant: "destructive",
          });
          navigate("/");
        });
      return;
    }

    // ── Error forwarded from Google or backend ────────────────────────────────
    if (error) {
      toast({
        title: "Google sign-in failed",
        description: error,
        variant: "destructive",
      });
      navigate("/");
      return;
    }

    // ── Legacy Supabase OAuth flow (no VITE_GOOGLE_CLIENT_ID) ─────────────────
    // Supabase processes the #access_token hash asynchronously; listen for it.
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "SIGNED_IN" && session) {
        subscription.unsubscribe();
        try {
          await exchangeSupabaseTokenForDjango(session);
          toast({
            title: "Welcome!",
            description: `Signed in as ${session.user.email}`,
          });
        } catch {
          // Django backend unavailable — session still valid via Supabase
        }
        navigate("/dashboard");
      } else if (event === "SIGNED_OUT") {
        subscription.unsubscribe();
        toast({
          title: "Google sign-in failed",
          description: "Session was not established. Please try again.",
          variant: "destructive",
        });
        navigate("/");
      }
    });

    // Fallback: if onAuthStateChange never fires within 10s, redirect home
    const fallbackTimer = setTimeout(() => {
      subscription.unsubscribe();
      toast({
        title: "Sign-in timed out",
        description: "Please try signing in again.",
        variant: "destructive",
      });
      navigate("/");
    }, 10_000);

    return () => {
      clearTimeout(fallbackTimer);
      subscription.unsubscribe();
    };
  }, [navigate, toast]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center space-y-4">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <h2 className="text-xl font-semibold text-foreground">
          Completing sign in...
        </h2>
        <p className="text-muted-foreground">
          Please wait while we sign you in with Google.
        </p>
      </div>
    </div>
  );
}
