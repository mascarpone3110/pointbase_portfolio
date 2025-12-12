from rest_framework.permissions import BasePermission


class IsTeacherOrAdmin(BasePermission):
    """Teacher または Admin のみ許可"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = request.user.profile.role
        return role in ["teacher", "admin"]
