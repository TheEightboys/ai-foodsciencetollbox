from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MembershipTier, UserMembership
from .serializers import MembershipTierSerializer, UserMembershipSerializer, MembershipUpgradeSerializer
from .services import GenerationLimitService


class MembershipTierListView(generics.ListAPIView):
    queryset = MembershipTier.objects.filter(is_active=True).order_by('display_order')
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        """
        Override list to ensure we always return an array, even if empty.
        """
        response = super().list(request, *args, **kwargs)
        # Ensure response.data is always an array
        if not isinstance(response.data, list):
            # If it's wrapped, try to extract
            if hasattr(response.data, 'results'):
                response.data = response.data['results']
            elif isinstance(response.data, dict) and 'results' in response.data:
                response.data = response.data['results']
            else:
                # Force to array
                response.data = list(response.data) if response.data else []
        return response


class UserMembershipDetailView(generics.RetrieveAPIView):
    serializer_class = UserMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            return self.request.user.membership
        except UserMembership.DoesNotExist:
            # If membership doesn't exist, create a default trial membership
            from apps.memberships.models import MembershipTier
            from django.utils import timezone
            from datetime import timedelta
            
            try:
                trial_tier = MembershipTier.objects.filter(name='trial').first()
                if not trial_tier:
                    # If trial tier doesn't exist, get the first active tier
                    trial_tier = MembershipTier.objects.filter(is_active=True).first()
                
                if trial_tier:
                    membership = UserMembership.objects.create(
                        user=self.request.user,
                        tier=trial_tier,
                        status='trialing',
                        current_period_start=timezone.now().date(),
                        current_period_end=None  # Trial has no renewal date
                    )
                    return membership
                
                # If no tiers exist, create a default trial tier
                # No tiers found, creating default trial tier
                trial_tier = MembershipTier.objects.create(
                    name='trial',
                    display_name='7-Day Trial',
                    description='Free trial with limited generations',
                    monthly_price=0.00,
                    generation_limit=10,
                    is_active=True,
                    display_order=0,
                    features=['10 generations', 'Word Downloads']
                )
                membership = UserMembership.objects.create(
                    user=self.request.user,
                    tier=trial_tier,
                    status='trialing',
                    current_period_start=timezone.now().date(),
                    current_period_end=(timezone.now() + timedelta(days=7)).date()  # Trial is 7 days
                )
                return membership
            except Exception as e:
                logger.error(f"Error creating membership: {e}", exc_info=True)
                from rest_framework.exceptions import NotFound
                raise NotFound(f"Unable to create membership: {str(e)}")


class MembershipUpgradeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        serializer = MembershipUpgradeSerializer(data=request.data)
        if serializer.is_valid():
            tier_id = serializer.validated_data['tier_id']
            try:
                tier = MembershipTier.objects.get(id=tier_id, is_active=True)
                
                # Check if tier has a Stripe price ID configured
                # First check the DB value, then fall back to the env-var STRIPE_PRO_PRICE_ID
                price_id = tier.stripe_price_id
                if not price_id and tier.name == 'pro':
                    from django.conf import settings as _settings
                    price_id = getattr(_settings, 'STRIPE_PRO_PRICE_ID', '')
                    if price_id and not tier.stripe_price_id:
                        # Persist so future calls skip the env lookup
                        tier.stripe_price_id = price_id
                        tier.save(update_fields=['stripe_price_id'])

                if not price_id:
                    logger.error(f"Stripe price ID not configured for tier: {tier.name} (ID: {tier.id})")
                    return Response({
                        'error': f'Stripe price ID not configured for {tier.display_name}.',
                        'detail': 'Set the STRIPE_PRO_PRICE_ID environment variable on Render, then redeploy.',
                        'tier_name': tier.name,
                        'tier_id': tier.id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create Stripe checkout session
                try:
                    from apps.payments.stripe_service import StripeService
                    from django.conf import settings
                    
                    # Verify Stripe is configured before attempting checkout
                    if not getattr(settings, 'STRIPE_SECRET_KEY', ''):
                        return Response({
                            'error': 'Stripe payments are not configured on this server.',
                            'detail': 'Please set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, and STRIPE_WEBHOOK_SECRET as environment variables on Render, then redeploy.',
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
                    # Build success and cancel URLs
                    frontend_url = settings.FRONTEND_URL
                    success_url = f"{frontend_url}/account/billing?session_id={{CHECKOUT_SESSION_ID}}"
                    cancel_url = f"{frontend_url}/pricing"
                    
                    checkout_session = StripeService.create_checkout_session(
                        user=request.user,
                        price_id=price_id,
                        success_url=success_url,
                        cancel_url=cancel_url
                    )
                    
                    return Response({
                        'checkout_url': checkout_session.url,
                        'checkout_session_id': checkout_session.id,
                        'message': f'Redirecting to checkout for {tier.display_name}'
                    }, status=status.HTTP_200_OK)
                    
                except Exception as e:
                    logger.error(f"Error creating Stripe checkout session: {e}", exc_info=True)
                    return Response({
                        'error': f'Failed to create checkout session: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            except MembershipTier.DoesNotExist:
                return Response({
                    'error': 'Invalid membership tier'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsageStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            membership = request.user.membership
            return Response({
                'can_generate_content': membership.can_generate_content,
                'generations_used': membership.generations_used_this_month,
                'remaining_generations': membership.remaining_generations,
                'tier_limit': membership.tier.generation_limit,
                'tier_name': membership.tier.display_name
            })
        except UserMembership.DoesNotExist:
            return Response({
                'can_generate_content': False,
                'generations_used': 0,
                'remaining_generations': 0,
                'tier_limit': 0,
                'tier_name': 'None'
            }, status=status.HTTP_200_OK)