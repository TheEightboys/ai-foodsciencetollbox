from rest_framework import permissions


class IsEmailVerified(permissions.BasePermission):
    """
    Custom permission to only allow verified users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.teacher_profile.email_verified


class IsAcademyMember(permissions.BasePermission):
    """
    Custom permission to only allow academy members.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.teacher_profile.is_academy_member