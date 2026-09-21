from django.apps import AppConfig
import sys

class SchoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schools'

    def ready(self):
        # Auto-seed initial data on startup if database is empty
        try:
            from schools.models import School
            if not School.objects.filter(code='211010').exists():
                import os
                from django.core.management import call_command
                fixture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'initial_data.json')
                if os.path.exists(fixture_path):
                    call_command('loaddata', fixture_path)
        except Exception as e:
            pass
