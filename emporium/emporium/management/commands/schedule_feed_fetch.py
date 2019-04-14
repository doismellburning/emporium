import django_rq
from django.core.management.base import BaseCommand

from emporium.jobs import fetch_and_create_recent_packages


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        job = django_rq.enqueue(fetch_and_create_recent_packages)
        self.stdout.write("Queued fetch_and_create_recent_packages: %s" % job)
