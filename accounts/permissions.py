"""
accounts/permissions.py
Role-based permission classes for CONNECT TO BUILD
"""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allow access only to House Owner role."""
    message = "Access restricted to House Owners."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'OWNER'
        )


class IsWorker(BasePermission):
    """Allow access only to Worker / Service Provider role."""
    message = "Access restricted to Workers / Service Providers."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'WORKER'
        )


class IsOwnerOrWorker(BasePermission):
    """Allow access to both Owner and Worker roles (not admin-only)."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('OWNER', 'WORKER')
        )


class IsProjectOwner(BasePermission):
    """Object-level: only the owner of a project can access it."""
    message = "You do not have permission to access this project."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.role != 'OWNER':
            return False
        if hasattr(obj, 'owner'):
            return obj.owner.user == request.user
        if hasattr(obj, 'project'):
            return obj.project.owner.user == request.user
        return False


class IsOwnWorkerProfile(BasePermission):
    """Object-level: worker can only modify their own profile."""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.role != 'WORKER':
            return False
        return obj.user == request.user
