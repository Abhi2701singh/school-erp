from django.apps import AppConfig

class SchoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schools'

    def ready(self):
        try:
            from schools.seed_data import seed_default_records
            seed_default_records()
        except Exception:
            pass
