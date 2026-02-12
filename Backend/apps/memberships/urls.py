from django.urls import path
from .views import (
    MembershipTierListView,
    UserMembershipDetailView,
    MembershipUpgradeView,
    UsageStatsView
)

app_name = 'memberships'

urlpatterns = [
    path('tiers/', MembershipTierListView.as_view(), name='tier-list'),
    path('membership/', UserMembershipDetailView.as_view(), name='membership-detail'),
    path('upgrade/', MembershipUpgradeView.as_view(), name='membership-upgrade'),
    path('usage-stats/', UsageStatsView.as_view(), name='usage-stats'),
]