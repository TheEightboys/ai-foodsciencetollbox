import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { membershipService } from '@/lib/api/memberships';
import { authService } from '@/lib/api/auth';

type SubscriptionTier = 'trial' | 'starter' | 'pro';

interface Profile {
  display_name: string | null;
  email: string | null;
  subscription_tier: SubscriptionTier | null;
  generation_count: number | null;
  generation_limit: number | null;
  subscription_start_date: string | null;
  subscription_end_date: string | null;
  billing_interval: 'month' | 'year' | null;
}

export function useProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) {
        setProfile(null);
        setLoading(false);
        return;
      }

      try {
        // Fetch user profile and membership info
        const [userProfile, membership] = await Promise.all([
          authService.getProfile(),
          membershipService.getCurrentMembership(),
        ]);

        // Handle generation_limit: null means unlimited, convert to -1 for frontend
        const generationLimit = membership.tier.generation_limit === null 
          ? -1  // -1 means unlimited in frontend
          : (membership.tier.generation_limit ?? 10);
        
        // Calculate billing interval from period dates if not provided
        let billingInterval: 'month' | 'year' | null = membership.billing_interval || null;
        if (!billingInterval && membership.current_period_start && membership.current_period_end) {
          const startDate = new Date(membership.current_period_start);
          const endDate = new Date(membership.current_period_end);
          const daysDiff = Math.round((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
          // If period is around 365 days, it's yearly; otherwise monthly
          if (daysDiff >= 300) {
            billingInterval = 'year';
          } else if (daysDiff >= 25) {
            billingInterval = 'month';
          }
        }
        
        setProfile({
          display_name: userProfile.display_name || `${userProfile.first_name || ''} ${userProfile.last_name || ''}`.trim() || null,
          email: userProfile.email || null,
          subscription_tier: (membership.tier.name.toLowerCase() as SubscriptionTier) || 'trial',
          generation_count: membership.generations_used_this_month ?? 0,
          generation_limit: generationLimit,
          subscription_start_date: membership.current_period_start || null,
          subscription_end_date: membership.current_period_end || null,
          billing_interval: billingInterval,
        });
      } catch (error) {
        // If membership doesn't exist, set default values
        try {
          const userProfile = await authService.getProfile();
          setProfile({
            display_name: userProfile.display_name || `${userProfile.first_name || ''} ${userProfile.last_name || ''}`.trim() || null,
            email: userProfile.email || null,
            subscription_tier: 'trial' as SubscriptionTier,
            generation_count: 0,
            generation_limit: 10,
            subscription_start_date: null,
            subscription_end_date: null,
            billing_interval: null,
          });
        } catch (profileError) {
          // If profile also fails, set null
          setProfile(null);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [user]);

  const remainingGenerations = profile 
    ? (profile.generation_limit === -1 
        ? -1 
        : (profile.generation_limit || 10) - (profile.generation_count || 0))
    : 0;

  return { 
    profile, 
    loading,
    remainingGenerations,
    isUnlimited: profile?.generation_limit === -1,
  };
}
