from django.urls import path
from .views import (
    AdminDashboardStatsView,
    MembershipTierListView,
    MembershipTierDetailView,
    UserMembershipListView,
    UserMembershipDetailView,
    PaymentHistoryListView,
    UserListView,
    UserCreateView,
    UserMembershipAssignView
)

app_name = 'admin_dashboard'

urlpatterns = [
    path('stats/', AdminDashboardStatsView.as_view(), name='dashboard-stats'),
    path('membership-tiers/', MembershipTierListView.as_view(), name='membership-tier-list'),
    path('membership-tiers/<int:pk>/', MembershipTierDetailView.as_view(), name='membership-tier-detail'),
    path('user-memberships/', UserMembershipListView.as_view(), name='user-membership-list'),
    path('user-memberships/<int:pk>/', UserMembershipDetailView.as_view(), name='user-membership-detail'),
    path('payment-history/', PaymentHistoryListView.as_view(), name='payment-history-list'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:user_id>/assign-membership/', UserMembershipAssignView.as_view(), name='user-assign-membership'),
]