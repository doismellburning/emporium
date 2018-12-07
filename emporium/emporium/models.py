from django.db import models

import requests

from . import sdist


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

    def fetch_sdist_url(self) -> str:
        """
        Fetches the URL of the sdist from PyPI, or None if any kind of issue
        """
        resp = requests.get(
            "https://pypi.org/pypi/%s/%s/json" % (self.package.name, self.version)
        )
        resp.raise_for_status()

        try:
            release = resp.json()["releases"][self.version]

            for release_file in release:
                if release_file["packagetype"] == "sdist":
                    return release_file["url"]
        except (KeyError, IndexError):
            return None

    def fetch_setuppy(self) -> str:
        """
        Fetches and saves and returns the sdist's setup.py, if it can be found
        """

        sdist_url = self.fetch_sdist_url()

        # TODO Fewer hacks, fewer assumptions, more modularity

        resp = requests.get(sdist_url)
        resp.raise_for_status()

        setuppy = sdist.extract_setuppy(resp.content, self.package.name, self.version)

        self.setuppy = setuppy

        if setuppy:
            self.fetched = True

        self.save()
