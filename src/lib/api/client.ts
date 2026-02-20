import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

/**
 * Determines the API base URL based on environment configuration.
 * 
 * Priority:
 * 1. VITE_API_BASE_URL environment variable (if set) - for production deployments with separate backend
 * 2. Development mode: '/api' (uses Vite proxy)
 * 3. Production fallback: Construct from current origin (same domain/subdomain)
 * 
 * For production with backend on a subdomain, set VITE_API_BASE_URL to your backend URL.
 * Example: VITE_API_BASE_URL=https://api.yourdomain.com
 * 
 * @returns The API base URL string
 */
const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (envUrl) {
    // Remove trailing slashes and ensure it doesn't already end with /api
    const cleanUrl = envUrl.replace(/\/+$/, '');
    // If it already ends with /api, return as is, otherwise add /api
    return cleanUrl.endsWith('/api') ? cleanUrl : `${cleanUrl}/api`;
  }
  
  // Development mode uses Vite proxy
  if (import.meta.env.DEV) {
    return '/api';
  }
  
  // Production: Use same origin (backend should be on same domain/subdomain)
  // This assumes backend is served from the same domain with /api prefix
  // OR backend is on a subdomain and you should set VITE_API_BASE_URL
  if (typeof window !== 'undefined') {
    const origin = window.location.origin;
    return `${origin}/api`;
  }
  
  // SSR fallback
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

// Debug logging removed for production - use browser dev tools network tab instead

/**
 * HTTP request timeout in milliseconds.
 * Default: 120 seconds — AI generation with validation/repair can need multiple LLM calls.
 */
const REQUEST_TIMEOUT_MS = 120000;

/**
 * Storage keys for authentication tokens.
 */
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
} as const;

/**
 * Creates and configures an Axios instance for API requests.
 * 
 * Features:
 * - Automatic JWT token injection
 * - Token refresh on 401 errors
 * - Request/response interceptors
 * - Consistent error handling
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: REQUEST_TIMEOUT_MS,
});

/**
 * Request interceptor: Injects Django JWT. If the backend was sleeping during
 * sign-in, a Supabase token may be pending exchange — try that now (lazy exchange).
 */
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    let token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);

    // Lazy Django token exchange: attempt once when no Django token is stored
    // but a Supabase token was saved as a fallback during sign-in.
    if (!token) {
      const pendingSupabaseToken = localStorage.getItem('supabase_pending_token');
      if (pendingSupabaseToken) {
        try {
          const baseUrl = (config.baseURL || API_BASE_URL).replace(/\/+$/, '');
          const resp = await fetch(`${baseUrl}/accounts/supabase-token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ supabase_token: pendingSupabaseToken }),
          });
          if (resp.ok) {
            const data = await resp.json();
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access);
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh);
            localStorage.removeItem('supabase_pending_token');
            token = data.access;
          }
        } catch {
          // Backend still unavailable — proceed without token (will get 401/403)
        }
      }
    }

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: Handles token refresh on 401 errors.
 * 
 * Flow:
 * 1. On 401 error, attempt to refresh the access token
 * 2. If refresh succeeds, retry the original request with new token
 * 3. If refresh fails, clear tokens and redirect to login
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle network errors (backend not reachable)
    if (!error.response && error.code !== 'ERR_CANCELED') {
      const isProduction = !import.meta.env.DEV;
      
      // Enhanced error message without exposing API URLs
      let errorMessage: string;
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        errorMessage = isProduction
          ? 'Cannot connect to server. Please check your network connection or contact support.'
          : 'Cannot connect to server. Please ensure the backend is running.';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. The server may be slow or unavailable. Please try again.';
      } else {
        errorMessage = isProduction
          ? 'Connection error. Please check your network or contact support.'
          : 'Connection error. Please check if the backend is running.';
      }
      
      // Error logging removed for production - errors are handled via user-facing messages
      
      // Enhance error message for better debugging
      const enhancedError = new Error(
        error.message || errorMessage
      ) as AxiosError;
      enhancedError.code = error.code;
      enhancedError.config = error.config;
      return Promise.reject(enhancedError);
    }

    // Handle 401 Unauthorized: token expired or invalid
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Use axios directly to avoid circular dependency
        const response = await axios.post<{ access: string }>(
          `${API_BASE_URL}/accounts/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access);

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`;
        }

        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed: clear tokens.
        // Do NOT hard-redirect — the React auth context will detect the
        // missing user and show the login UI without a full page reload.
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

