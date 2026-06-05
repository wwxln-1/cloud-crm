"""Reusable Role Based Access Control helpers for views and the API."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrReadOnly(BasePermission):
    """Read for any authenticated user; writes only for Manager/Admin."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_manager_role


class IsAdminRole(BasePermission):
    """Full access reserved for Admin role / superusers (e.g. user mgmt)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_role)
