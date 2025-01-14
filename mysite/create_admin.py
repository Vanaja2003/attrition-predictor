import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

# Create or update the admin user
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("Admin password updated successfully!")
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Admin user created successfully!")

print("\nYou can now log in with:")
print("Username: admin")
print("Password: admin123")
