import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { handleSupabaseGoogleCallback } from "@/lib/api/supabaseAuth";
import { useToast } from "@/hooks/use-toast";

export default function GoogleCallback() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const hasRun = useRef(false);

  useEffect(() => {
    // Prevent double-execution in React Strict Mode
    if (hasRun.current) return;
    hasRun.current = true;

    const finishSignIn = async () => {
      try {
        const djangoAuth = await handleSupabaseGoogleCallback();
        // onAuthStateChange in AuthContext will update user state automatically.
        // Just show a welcome toast and redirect to the dashboard.
        toast({
          title: "Welcome!",
          description: `Signed in as ${djangoAuth.user.email}`,
        });
        navigate("/dashboard");
      } catch (err) {
        const e = err as Error;
        toast({
          title: "Google sign-in failed",
          description: e.message || "Please try again.",
          variant: "destructive",
        });
        navigate("/");
      }
    };

    finishSignIn();
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
