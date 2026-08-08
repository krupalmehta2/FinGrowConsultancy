"""Populate safe, repeatable demo content for ephemeral hosting environments."""

import runpy

from django.conf import settings
from django.core.management.base import BaseCommand

from website.models import WebsiteSettings


class Command(BaseCommand):
    help = "Seed the demo services and create default website settings if missing."

    def handle(self, *args, **options):
        runpy.run_path(str(settings.BASE_DIR / "seed.py"), run_name="__main__")
        WebsiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "company_name": "FinGrow Consultancy Services",
                "meta_title": "FinGrow Consultancy Services | Financial & Incubation Scheme Advisory",
                "meta_description": "Expert financial advisory, business consulting and incubation scheme guidance for founders and businesses across India.",
            },
        )
        self.stdout.write(self.style.SUCCESS("Demo content and website settings are ready."))
