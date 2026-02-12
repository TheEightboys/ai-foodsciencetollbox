from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CreatePaymentIntentView,
    CreateCustomerPortalSessionView,
    PaymentHistoryListView,
    StripeWebhookView
)
from .webhooks import stripe_webhook

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('create-customer-portal-session/', CreateCustomerPortalSessionView.as_view(), name='create-customer-portal-session'),
    path('payment-history/', PaymentHistoryListView.as_view(), name='payment-history'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]