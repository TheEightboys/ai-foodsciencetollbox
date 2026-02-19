/**
 * Supabase-backed auth service.
 *
 * Flow:
 *  1. User signs in / signs up via Supabase (email+password or Google OAuth).
 *  2. Supabase returns a session with an access_token.
 *  3. We POST that token to /api/accounts/supabase-token/ on the Django backend.
 *  4. Django verifies the token (calls Supabase /auth/v1/user), creates/gets the
 *     local Django user, and returns its own access+refresh JWT pair.
 *  5. We store those Django tokens in localStorage exactly as before.
 *
 * If the Django backend is sleeping (Render free tier cold start / 502), sign-in
 * still completes immediately using Supabase session data. The Django token exchange
 * is retried lazily by apiClient before the first real API call.
 */
import type { Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import apiClient from './client';

export interface DjangoAuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
}

/** How long to wait for the Django backend before falling back to Supabase-only auth. */
const EXCHANGE_TIMEOUT_MS = 8_000;

/** localStorage key for a Supabase token pending Django exchange. */
export const SUPABASE_PENDING_TOKEN_KEY = 'supabase_pending_token';

/** Exchange a Supabase access token for a Django JWT pair. */
async function exchangeSupabaseToken(supabaseAccessToken: string): Promise<DjangoAuthResponse> {
  const response = await apiClient.post<DjangoAuthResponse>('/accounts/supabase-token/', {
    supabase_token: supabaseAccessToken,
  });
  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);
  localStorage.removeItem(SUPABASE_PENDING_TOKEN_KEY);
  return response.data;
}

/**
 * Build a fallback DjangoAuthResponse from a Supabase session when the backend
 * is unavailable. Stores the token for lazy exchange later.
 */
function buildFallbackAuth(session: Session): DjangoAuthResponse {
  const meta = session.user?.user_metadata || {};
  const fullName: string = meta.full_name || '';
  const parts = fullName.trim().split(/\s+/);
  localStorage.setItem(SUPABASE_PENDING_TOKEN_KEY, session.access_token);
  return {
    access: '',
    refresh: '',
    user: {
      id: 0,
      email: session.user?.email || '',
      first_name: meta.first_name || meta.given_name || parts[0] || '',
      last_name: meta.last_name || meta.family_name || parts.slice(1).join(' ') || '',
    },
  };
}

/**
 * Try to exchange a Supabase token within EXCHANGE_TIMEOUT_MS.
 * On timeout or backend error, fall back to Supabase-only auth (non-blocking).
 */
async function exchangeOrFallback(session: Session): Promise<DjangoAuthResponse> {
  const timeout = new Promise<never>(
    (_, reject) => setTimeout(() => reject(new Error('timeout')), EXCHANGE_TIMEOUT_MS)
  );
  try {
    return await Promise.race([exchangeSupabaseToken(session.access_token), timeout]);
  } catch {
    // Backend unavailable — sign user in with Supabase data; apiClient will retry
    return buildFallbackAuth(session);
  }
}

/** Sign in with email and password via Supabase, then get Django JWT (non-blocking). */
export async function supabaseSignIn(email: string, password: string): Promise<DjangoAuthResponse> {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw new Error(error.message);
  if (!data.session) throw new Error('No session returned from Supabase');
  return exchangeOrFallback(data.session);
}

/** Sign up with email and password via Supabase, then get Django JWT (non-blocking). */
export async function supabaseSignUp(
  email: string,
  password: string,
  firstName: string,
  lastName: string
): Promise<{ message: string; user?: DjangoAuthResponse['user'] }> {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: { first_name: firstName, last_name: lastName, full_name: `${firstName} ${lastName}` },
    },
  });

  if (error) throw new Error(error.message);

  // Supabase may require email confirmation. If a session exists, exchange immediately.
  if (data.session) {
    const djangoAuth = await exchangeOrFallback(data.session);
    return {
      message: 'Account created successfully.',
      user: djangoAuth.user,
    };
  }

  // Email confirmation required
  return {
    message: 'Account created! Please check your email to confirm your address before signing in.',
  };
}

/** Initiate Google OAuth via Supabase (redirects the browser). */
export async function supabaseSignInWithGoogle(): Promise<void> {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/google/callback`,
      queryParams: { prompt: 'select_account' },
    },
  });
  if (error) throw new Error(error.message);
}

/**
 * Called on the /auth/google/callback page after Supabase redirects back.
 * Picks up the session from the URL hash, then exchanges for a Django JWT.
 */
export async function handleSupabaseGoogleCallback(): Promise<DjangoAuthResponse> {
  const { data, error } = await supabase.auth.getSession();
  if (error) throw new Error(error.message);
  if (!data.session) throw new Error('No session found after Google sign-in');
  return exchangeOrFallback(data.session);
}

/** Sign out from both Supabase and clear Django tokens. */
export async function supabaseSignOut(): Promise<void> {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem(SUPABASE_PENDING_TOKEN_KEY);
  await supabase.auth.signOut();
}

/** Restore an existing Supabase session on app load and refresh the Django token. */
export async function restoreSupabaseSession(): Promise<DjangoAuthResponse | null> {
  const { data } = await supabase.auth.getSession();
  if (!data.session) return null;
  return exchangeOrFallback(data.session);
}
