from rest_framework import permissions


class IsStaffAdmin(permissions.BasePermission):
    """
    Custom permission to only allow staff admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff