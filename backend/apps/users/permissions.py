"""
Custom DRF permissions implementing RBAC.
"""
from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdminUser(BasePermission):
    """Allow access only to users with role=admin."""
    message = 'Administrator access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsAdminOrManager(BasePermission):
    """Allow access to admins and managers."""
    message = 'Administrator or Manager access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRole.ADMIN, UserRole.MANAGER]
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access if the user owns the object or is admin."""
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.ADMIN:
            return True
        # Support both obj.user and obj directly being a user
        owner = getattr(obj, 'user', obj)
        return owner == request.user
