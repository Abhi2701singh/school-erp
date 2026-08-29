import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_erp.settings')
django.setup()

from accounts.models import User

def seed():
    print("Setting up Super Admin account...")

    # 1. Super Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@edumanage.com', 'admin123', role=User.Roles.SUPER_ADMIN)
        print("Super Admin created: admin / admin123")
    else:
        admin_user = User.objects.get(username='admin')
        admin_user.role = User.Roles.SUPER_ADMIN
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.set_password('admin123')
        admin_user.save()
        print("Super Admin verified & password updated to: admin123")

    print("Setup completed successfully!")

if __name__ == '__main__':
    seed()
