from datetime import date
from django.core.management.base import BaseCommand
from concert.models import Concert


class Command(BaseCommand):
    help = "Add fictional demonstration concerts without changing existing records."

    def handle(self, *args, **options):
        for name, city, when in [
            ("Djirection — Winter Live", "London", date(2026, 12, 12)),
            ("Djirection — New Year Sessions", "Dublin", date(2027, 1, 16)),
        ]:
            Concert.objects.get_or_create(concert_name=name, defaults={"city": city, "date": when, "duration": 2})
        self.stdout.write(self.style.SUCCESS(f"Concerts available: {Concert.objects.count()}"))
