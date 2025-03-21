# DRF Imports
from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    Custom permission that allows access only to object owners.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
