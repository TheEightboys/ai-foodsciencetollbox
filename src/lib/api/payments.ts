import apiClient from './client';

export interface PaymentHistory {
  id: number;
  amount: string;
  currency: string;
  status: 'succeeded' | 'failed' | 'pending';
  description: string;
  created_at: string;
  stripe_payment_intent_id: string;
}

export interface CheckoutSessionRequest {
  price_id: string;
  success_url: string;
  cancel_url: string;
}

export interface CheckoutSessionResponse {
  checkout_session_id: string;
  checkout_url: string;
}

class PaymentService {
  async createCheckoutSession(data: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
    const response = await apiClient.post<CheckoutSessionResponse>(
      '/payments/create-checkout-session/',
      data
    );
    return response.data;
  }

  async getPaymentHistory(params?: {
    page?: number;
    page_size?: number;
  }): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: PaymentHistory[];
  }> {
    const response = await apiClient.get('/payments/payment-history/', { params });
    return response.data;
  }

  async createCustomerPortalSession(returnUrl: string): Promise<{ portal_url: string }> {
    const response = await apiClient.post<{ portal_url: string }>(
      '/payments/create-customer-portal-session/',
      { return_url: returnUrl }
    );
    return response.data;
  }
}

export const paymentService = new PaymentService();

