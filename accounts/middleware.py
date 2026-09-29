from accounts.models import set_current_school
from schools.models import School

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
                if not active_school:
                    active_school = request.user.school or School.objects.first()
            else:
                active_school = request.user.school or School.objects.first()
        else:
            active_school = School.objects.first()

        # If no school exists in database, initialize a default School
        if not active_school:
            active_school, _ = School.objects.get_or_create(
                code="PN_NPS",
                defaults={
                    "name": "PN National Public School",
                    "address": "Gorakhpur, Uttar Pradesh",
                    "phone": "9876543210",
                    "email": "contact@pnnps.edu.in",
                    "principal_name": "Dr. Principal",
                    "affiliation_no": "CBSE-UP-2025",
                    "is_active": True
                }
            )

        set_current_school(active_school)
        request.school = active_school

        response = self.get_response(request)

        # Clear thread local context after request handling completes
        set_current_school(None)

        return response

