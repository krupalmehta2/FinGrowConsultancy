from datetime import datetime
from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a timestamped copy of the SQLite database in backups/."

    def handle(self, *args, **options):
        source = Path(settings.DATABASES["default"]["NAME"])
        destination_dir = settings.BASE_DIR / "backups"
        destination_dir.mkdir(exist_ok=True)
        destination = destination_dir / f"db-{datetime.now().strftime('%Y%m%d-%H%M%S')}.sqlite3"
        shutil.copy2(source, destination)
        self.stdout.write(self.style.SUCCESS(f"Database backup created: {destination}"))
