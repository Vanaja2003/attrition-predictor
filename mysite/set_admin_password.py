from django.contrib.auth.models import User
from django.core.wsgi import get_wsgi_application
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Create or update the admin user
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Admin user created successfully!")
else:
    user.set_password('admin123')  # Set password to 'admin123'
    user.save()
    print("Admin password updated successfully!")

print("\nYou can now log in with:")
print("Username: admin")
print("Password: admin123")
