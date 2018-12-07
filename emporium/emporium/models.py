from django.db import models

import requests


class Package(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name

    def fetch_latest_version(self) -> ("PackageVersion", bool):
        """
        Checks PyPI for the latest version, then get_or_create-s an appropriate PackageVersion
        """
        resp = requests.get("https://pypi.org/pypi/%s/json" % self.name)
        resp.raise_for_status()

        try:
            releases = resp.json()["releases"]
            latest_version = list(releases)[-1]
            pv = PackageVersion.objects.get_or_create(
                package=self, version=latest_version
            )
            return pv
        except (KeyError, IndexError):
            return None


class PackageVersion(models.Model):
    package = models.ForeignKey("package", on_delete=models.CASCADE)
    version = models.CharField(max_length=120)
    setuppy = models.TextField()
    fetched = models.BooleanField(default=False)

    def __str__(self):
        return str(self.package) + "-" + self.version
