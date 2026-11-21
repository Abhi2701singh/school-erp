from accounts.models import set_current_school
from schools.models import School

class TenantMiddleware:
    """
    Middleware that sets the current school tenant context in thread-local storage
    and request.school attribute based on authenticated user or session override.
    Strictly locks out sessions belonging to deactivated / inactive schools.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Bypass static and media assets
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        active_school = None
        try:
            if request.user.is_authenticated:
                is_super = False
                if callable(getattr(request.user, 'is_super_admin', None)):
                    is_super = request.user.is_super_admin()
                elif getattr(request.user, 'is_superuser', False):
                    is_super = True

                if not is_super:
                    # Non-superadmin user: check their school's active status
                    user_school = getattr(request.user, 'school', None)
                    if user_school and not user_school.is_active:
                        # Deactivated school: immediately intercept and terminate access
                        if request.path.startswith('/api/'):
                            from django.http import JsonResponse
                            return JsonResponse({
                                'error': f"The school branch '{user_school.name}' is currently deactivated by platform administration. Access is locked."
                            }, status=403)

                        if not request.path.startswith('/accounts/logout'):
                            from django.contrib.auth import logout
                            from django.contrib import messages
                            from django.shortcuts import redirect

                            logout(request)
                            if hasattr(request, '_messages'):
                                messages.error(
                                    request,
                                    f"Access Locked: Your school branch '{user_school.name}' is currently inactive / suspended by the platform administrator. Portal operations and access are disabled."
                                )
                            return redirect('login')

                    active_school = user_school or School.objects.filter(is_active=True).first()
                else:
                    # Super admin can switch context to any school (active or inactive audit)
                    session_school_id = request.session.get('active_school_id')
                    if session_school_id:
                        try:
                            active_school = School.objects.get(pk=session_school_id)
                        except School.DoesNotExist:
                            active_school = None
                    if not active_school:
                        active_school = request.user.school or School.objects.filter(is_active=True).first() or School.objects.first()
            else:
                active_school = School.objects.filter(is_active=True).first() or School.objects.first()
        except Exception as e:
            import sys
            print(f"[TENANT MIDDLEWARE WARNING] Failed to resolve active school tenant: {e}", file=sys.stderr)
            active_school = None

        set_current_school(active_school)
        request.school = active_school

        response = self.get_response(request)

        # Clear thread local context after request handling completes
        set_current_school(None)

        return response


