from django.test import TestCase


class UrlsTestCase(TestCase):
    def test_package_list(self):
        resp = self.client.get("/packages/", secure=True)
        assert resp.status_code == 200
