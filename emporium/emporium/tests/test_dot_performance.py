from django.test import TestCase
from django.urls import reverse

from emporium.models import Dependency, Package, PackageVersion


class TestDotPerformance(TestCase):
    def test_query_count(self):
        """
        Fetching the dependency graph should just be one query.

        One *HUGE* query, but still, one query.

        (Guess who accidentally did 2n queries because they forgot about template lookups)
        """
        p1 = Package.objects.create(name="p1")
        p2 = Package.objects.create(name="p2")
        pv1 = PackageVersion.objects.create(package=p1, version="1")
        Dependency.objects.create(
            package_version=pv1, package=p2, specification=p2.name
        )
        Dependency.objects.create(
            package_version=pv1, package=p2, specification=p2.name
        )

        with self.assertNumQueries(1):
            response = self.client.get(reverse("dot"), secure=True)
            self.assertContains(response, "digraph")
