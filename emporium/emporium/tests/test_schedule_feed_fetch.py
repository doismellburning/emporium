from django.core.management import call_command
from django.test import TestCase


class TestScheduleFeedFetch(TestCase):
    def test_command(self):
        call_command("schedule_feed_fetch")
