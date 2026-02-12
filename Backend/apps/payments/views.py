import stripe
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import PaymentHistory
from .serializers import PaymentHistorySerializer
from .stripe_service import StripeService
from .webhooks import stripe_webhook

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            price_id = request.data.get('price_id')
            success_url = request.data.get('success_url')
            cancel_url = request.data.get('cancel_url')
            
            if not all([price_id, success_url, cancel_url]):
                return Response({
                    'error': 'Missing required parameters: price_id, success_url, cancel_url'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            checkout_session = StripeService.create_checkout_session(
                user=request.user,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return Response({
                'checkout_session_id': checkout_session.id,
                'checkout_url': checkout_session.url
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amount = request.data.get('amount')
            currency = request.data.get('currency', 'usd')
            description = request.data.get('description', '')
            
            if not amount:
                return Response({
                    'error': 'Amount is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            payment_intent = StripeService.create_payment_intent(
                user=request.user,
                amount=float(amount),
                currency=currency,
                description=description
            )
            
            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryListView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentHistory.objects.filter(user=self.request.user)


class CreateCustomerPortalSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            return_url = request.data.get('return_url')
            
            if not return_url:
                return Response({
                    'error': 'return_url is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            portal_session = StripeService.create_customer_portal_session(
                user=request.user,
                return_url=return_url
            )
            
            return Response({
                'portal_url': portal_session.url
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Stripe webhook endpoint.
    Uses the webhook handler from webhooks.py
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return stripe_webhook(request)