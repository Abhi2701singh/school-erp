from accounts.models import set_current_school, set_current_school, School

class TenantMiddleware:
    """
    Middleware that sets the current school tenant context in thread-local storage
    and request.school attribute based on authenticated user or session override.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        active_school = None
        if request.user.is_authenticated:
            if request.user.is_super_admin():
                # Allow super admin to switch schools via session 'active_school_id'
                session_school_id = request.session.get('active_school_id')
                if session_school_id:
                    try:
                        active_school = School.objects.get(pk=session_school_id)
                    except School.DoesNotExist:
                        active_school = None
                else:
                    active_school = None
            else:
                active_school = request.user.school

        set_current_school(active_school)
        request.school = active_school

        response = self.get_response(request)

        # Clear thread local context after request handling completes
        set_current_school(None)

        return response
