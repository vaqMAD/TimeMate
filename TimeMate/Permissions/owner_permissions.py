# Permissions error codes
PERMISSION_ERROR_CODE_NOT_TASK_OWNER = "not_task_owner"
# DRF Imports
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsObjectOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner != request.user:
            raise PermissionDenied(
                detail="You do not have permission to access this task",
                code=PERMISSION_ERROR_CODE_NOT_TASK_OWNER
            )
        return True
