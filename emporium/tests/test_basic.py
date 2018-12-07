from django.test import TestCase


class BasicTestCase(TestCase):
    def test_getting_root(self):
        self.client.get('/')
