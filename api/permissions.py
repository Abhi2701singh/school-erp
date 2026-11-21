from rest_framework import permissions

class IsActiveSchoolUser(permissions.BasePermission):
    """
    Blocks any API request from users belonging to an inactive school branch.
    Super Admins are exempt.
    """
    message = "This school branch is currently deactivated by platform administration. Mobile app and portal access are disabled."

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return True  # Allow DRF's IsAuthenticated to handle unauthenticated requests cleanly

        is_super = getattr(user, 'is_superuser', False) or (callable(getattr(user, 'is_super_admin', None)) and user.is_super_admin())
        if is_super:
            return True

        user_school = getattr(user, 'school', None)
        if user_school and not user_school.is_active:
            return False

        return True
