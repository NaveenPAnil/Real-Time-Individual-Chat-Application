import os
from django.contrib.auth import get_user_model

User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')

if email and password:
    if not User.objects.filter(email=email).exists():
        print(f"Creating superuser: {email}")
        User.objects.create_superuser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
    else:
        print(f"Superuser {email} already exists.")
else:
    print("Superuser credentials not found. Skipping.")