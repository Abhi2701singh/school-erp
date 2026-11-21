import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_erp.settings')
django.setup()

from accounts.models import User

def seed():
    print("Checking Super Admin account...")

    # 1. Super Admin: create only if no super admin exists
    if not User.objects.filter(role=User.Roles.SUPER_ADMIN).exists():
        User.objects.create_superuser('admin', 'admin@edumanage.com', 'admin123', role=User.Roles.SUPER_ADMIN)
        print("Super Admin created: admin / admin123")
    else:
        print("Super Admin already exists. Preserving existing credentials and data.")

    print("Setup completed successfully!")

if __name__ == '__main__':
    seed()
