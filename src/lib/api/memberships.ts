import apiClient from './client';

export interface MembershipTier {
  id: number;
  name: string;
  display_name: string;
  description: string;
  monthly_price: string;
  generation_limit: number | null;
  features: string[];
  is_active: boolean;
}

export interface UserMembership {
  id: number;
  tier: MembershipTier;
  status: 'active' | 'past_due' | 'canceled' | 'trialing';
  generations_used_this_month: number;
  current_period_start: string | null;
  current_period_end: string | null;
  billing_interval: 'month' | 'year' | null;
  remaining_generations: number | null;
  can_generate_content: boolean;
  generations_used?: number;
  generations_limit?: number;
  start_date?: string | null;
  end_date?: string | null;
}

class MembershipService {
  async getMembershipTiers(): Promise<MembershipTier[]> {
    try {
      const response = await apiClient.get<MembershipTier[]>('/memberships/tiers/');
      // Handle both direct array response and wrapped response
      if (Array.isArray(response.data)) {
        return response.data;
      }
      // If response is wrapped, try to extract the array
      if (response.data && Array.isArray(response.data.results)) {
        return response.data.results;
      }
      if (response.data && Array.isArray(response.data.data)) {
        return response.data.data;
      }
      // If it's a single object, wrap it in an array
      if (response.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
        return [response.data];
      }
      // Fallback: return empty array if we can't parse it
      // Invalid response format - handled by returning empty array
      return [];
    } catch (error: any) {
      // Error fetching tiers - rethrow for caller to handle
      throw error;
    }
  }

  async getCurrentMembership(): Promise<UserMembership> {
    const response = await apiClient.get<UserMembership>('/memberships/membership/');
    return response.data;
  }

  async upgradeMembership(tierId: number): Promise<{ checkout_url: string; checkout_session_id: string }> {
    const response = await apiClient.post('/memberships/upgrade/', { tier_id: tierId });
    return response.data;
  }

  async cancelMembership(): Promise<void> {
    await apiClient.post('/memberships/cancel/');
  }
}

export const membershipService = new MembershipService();

