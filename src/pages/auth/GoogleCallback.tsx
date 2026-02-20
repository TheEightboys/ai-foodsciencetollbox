import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import {
  exchangeSupabaseTokenForDjango,
  exchangeGoogleCode,
} from "@/lib/api/supabaseAuth";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/lib/api/client";

/**
 * Wake the backend before attempting the one-shot Google code exchange.
 * Render free-tier workers can be dead (OOM / cold start);
 * hitting /health/ first ensures a live worker is ready to handle the
 * token exchange without wasting the single-use Google auth code.
 *
 * Retries the health check up to `maxAttempts` times.
 */
async function ensureBackendReady(
  maxAttempts = 5,
  delayMs = 3000,
): Promise<void> {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      await apiClient.get("/health/", { timeout: 10_000 });
      return; // Backend is alive
    } catch {
      if (i === maxAttempts - 1)
        throw new Error("Backend is not responding. Please try again later.");
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}

export default function GoogleCallback() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const hasRun = useRef(false);
  const [statusMessage, setStatusMessage] = useState("Completing sign in...");

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const error = params.get("error");

    // ── Direct Google OAuth flow (VITE_GOOGLE_CLIENT_ID is set) ──────────────
    // Google redirected here with ?code=... — exchange it via the Django backend.
    //
    // IMPORTANT: Google auth codes are SINGLE-USE. We must NOT retry the
    // exchange call itself — if the backend consumes the code but crashes
    // before responding, the code is gone. Instead we first wake the backend
    // with a health check, then send the code exactly once.
    if (code) {
      (async () => {
        try {
          // Step 1: Make sure the backend worker is alive
          setStatusMessage("Waking up server...");
          await ensureBackendReady(5, 3000);

          // Step 2: Exchange the code (one attempt only — code is single-use)
          setStatusMessage("Completing sign in...");
          const auth = await exchangeGoogleCode(code);
          toast({
            title: "Welcome!",
            description: `Signed in as ${auth.user.email}`,
          });
          navigate("/dashboard");
        } catch (err: unknown) {
          const message =
            err instanceof Error ? err.message : "Google sign-in failed.";
          toast({
            title: "Google sign-in failed",
            description: message,
            variant: "destructive",
          });
          navigate("/");
        }
      })();
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
          {statusMessage}
        </h2>
        <p className="text-muted-foreground">
          Please wait while we sign you in with Google.
        </p>
        <p className="text-xs text-muted-foreground/60">
          This may take a moment if the server is waking up.
        </p>
      </div>
    </div>
  );
}
