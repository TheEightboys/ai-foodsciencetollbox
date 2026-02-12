import apiClient from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  email_verified?: boolean;
}

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string | null;
  date_joined: string;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/accounts/login/', credentials);
    const { access, refresh, user } = response.data;
    
    // Store tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  }

  async register(data: RegisterData): Promise<{ message: string; user?: { id: number; email: string; first_name: string; last_name: string } }> {
    const response = await apiClient.post<{ message: string; user?: { id: number; email: string; first_name: string; last_name: string } }>('/accounts/register/', data);
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    // Always clear tokens locally first
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Try to notify backend (non-blocking)
    if (refreshToken) {
      try {
        await apiClient.post('/accounts/logout/', { refresh: refreshToken });
      } catch (error) {
        // Ignore errors - tokens are already cleared locally
        // Backend logout is best-effort
      }
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/accounts/profile/');
    return response.data;
  }

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/accounts/profile/');
    return response.data;
  }

  async updateProfile(data: { first_name?: string; last_name?: string; display_name?: string }): Promise<UserProfile> {
    const response = await apiClient.patch<UserProfile>('/accounts/profile/', data);
    return response.data;
  }

  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // Use Django REST Framework SimpleJWT default endpoint
    const response = await apiClient.post<{ access: string }>('/accounts/token/refresh/', {
      refresh: refreshToken,
    });

    const { access } = response.data;
    localStorage.setItem('access_token', access);
    return access;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/accounts/reset-password/', {
      email,
    });
    return response.data;
  }

  async resetPassword(uid: string, token: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/accounts/reset-password-confirm/', {
      token: `${uid}/${token}`,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
    return response.data;
  }

  async resendVerificationEmail(): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/accounts/resend-verification-email/');
    return response.data;
  }

  async contactSupport(subject: string, message: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/accounts/contact-support/', {
      subject,
      message,
    });
    return response.data;
  }
}

export const authService = new AuthService();

