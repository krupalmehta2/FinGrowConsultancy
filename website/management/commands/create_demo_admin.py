"""Create the demo admin from Render environment variables without logging credentials."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the demo superuser from DEMO_ADMIN_* environment variables."

    def handle(self, *args, **options):
        username = os.getenv("DEMO_ADMIN_USERNAME")
        email = os.getenv("DEMO_ADMIN_EMAIL", "")
        password = os.getenv("DEMO_ADMIN_PASSWORD")
        if not username or not password:
            self.stdout.write("Demo admin skipped: DEMO_ADMIN_USERNAME/PASSWORD not configured.")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(update_fields=["email", "password", "is_staff", "is_superuser"])
        self.stdout.write(self.style.SUCCESS("Demo admin created/updated."))
