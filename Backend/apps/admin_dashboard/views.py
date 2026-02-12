from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, TeacherProfile
from apps.memberships.models import MembershipTier, UserMembership
from apps.payments.models import PaymentHistory
from apps.generators.models import GeneratedContent
from .serializers import (
    MembershipTierSerializer,
    UserMembershipSerializer,
    PaymentHistorySerializer,
    UserCreateSerializer,
    UserListSerializer
)

User = get_user_model()


class AdminDashboardStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Get counts
        total_users = User.objects.count()
        total_teachers = TeacherProfile.objects.filter(is_academy_member=True).count()
        total_payments = PaymentHistory.objects.count()
        total_generated_content = GeneratedContent.objects.count()
        
        # Get recent data
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_payments = PaymentHistory.objects.select_related('user').order_by('-created_at')[:5]
        recent_content = GeneratedContent.objects.select_related('user').order_by('-created_at')[:5]
        
        data = {
            'stats': {
                'total_users': total_users,
                'total_teachers': total_teachers,
                'total_payments': total_payments,
                'total_generated_content': total_generated_content,
            },
            'recent_users': [
                {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined
                }
                for user in recent_users
            ],
            'recent_payments': [
                {
                    'id': payment.id,
                    'user_email': payment.user.email,
                    'amount': float(payment.amount),
                    'status': payment.status,
                    'created_at': payment.created_at
                }
                for payment in recent_payments
            ],
            'recent_content': [
                {
                    'id': content.id,
                    'user_email': content.user.email,
                    'title': content.title,
                    'content_type': content.content_type,
                    'created_at': content.created_at
                }
                for content in recent_content
            ]
        }
        
        return Response(data)


class MembershipTierListView(generics.ListCreateAPIView):
    queryset = MembershipTier.objects.all().order_by('display_order')
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.IsAdminUser]


class MembershipTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MembershipTier.objects.all()
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.IsAdminUser]


class UserMembershipListView(generics.ListAPIView):
    queryset = UserMembership.objects.select_related('user', 'tier').all()
    serializer_class = UserMembershipSerializer
    permission_classes = [permissions.IsAdminUser]


class UserMembershipDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserMembership.objects.select_related('user', 'tier').all()
    serializer_class = UserMembershipSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentHistoryListView(generics.ListAPIView):
    queryset = PaymentHistory.objects.select_related('user').all()
    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAdminUser]


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        return queryset


class UserCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')
        password = serializer.validated_data.get('password')
        tier_name = serializer.validated_data.get('tier_name', 'trial')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate a random password if not provided
            if not password:
                import secrets
                password = secrets.token_urlsafe(12)
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            
            # Assign membership tier
            try:
                tier = MembershipTier.objects.get(name=tier_name)
            except MembershipTier.DoesNotExist:
                tier = MembershipTier.objects.filter(name='trial').first()
                if not tier:
                    tier = MembershipTier.objects.filter(is_active=True).first()
            
            if tier:
                # Get or create membership
                membership, created = UserMembership.objects.get_or_create(
                    user=user,
                    defaults={
                        'tier': tier,
                        'status': 'active' if tier_name != 'trial' else 'trialing',
                        'current_period_start': timezone.now().date(),
                        'current_period_end': (timezone.now() + timedelta(days=30)).date() if tier_name != 'trial' else (timezone.now() + timedelta(days=7)).date()
                    }
                )
                
                if not created:
                    # Update existing membership
                    membership.tier = tier
                    membership.status = 'active' if tier_name != 'trial' else 'trialing'
                    membership.save()
            
            logger.info(f"Admin created user {email} with tier {tier_name}")
            
            return Response({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tier': tier.display_name if tier else None
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            return Response({
                'error': f'Failed to create user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMembershipAssignView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, user_id):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        tier_name = request.data.get('tier_name')
        if not tier_name:
            return Response({
                'error': 'tier_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tier = MembershipTier.objects.get(name=tier_name)
        except MembershipTier.DoesNotExist:
            return Response({
                'error': f'Membership tier "{tier_name}" not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create membership
            membership, created = UserMembership.objects.get_or_create(
                user=user,
                defaults={
                    'tier': tier,
                    'status': 'active' if tier_name != 'trial' else 'trialing',
                    'current_period_start': timezone.now().date(),
                    'current_period_end': (timezone.now() + timedelta(days=30)).date() if tier_name != 'trial' else (timezone.now() + timedelta(days=7)).date()
                }
            )
            
            if not created:
                # Update existing membership
                membership.tier = tier
                membership.status = 'active' if tier_name != 'trial' else 'trialing'
                if tier_name != 'trial':
                    membership.current_period_end = (timezone.now() + timedelta(days=30)).date()
                membership.save()
            
            logger.info(f"Admin assigned tier {tier_name} to user {user.email}")
            
            return Response({
                'message': f'Membership tier updated to {tier.display_name}',
                'membership': UserMembershipSerializer(membership).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error assigning membership: {e}", exc_info=True)
            return Response({
                'error': f'Failed to assign membership: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)