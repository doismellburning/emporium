from typing import Iterable, Optional, Tuple

import requests
from django.db import models
from django.urls import reverse

from . import parser, sdist, validators


class Package(models.Model):
    name = models.CharField(
        max_length=120,
        unique=True,
        validators=[validators.validate_package_name_exists],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("package", kwargs={"name": self.name})

    def get_sorted_versions(self):
        return self.packageversion_set.all()  # TODO!

    def get_latest_version(self) -> Optional["PackageVersion"]:
        try:
            return self.packageversion_set.latest("version")
        except PackageVersion.DoesNotExist:
            return None

    def fetch_latest_version(self) -> Optional[Tuple["PackageVersion", bool]]:
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

    def fetch_all_versions(self) -> Iterable[Tuple["PackageVersion", bool]]:
        """
        Checks PyPI for the latest version, then get_or_create-s an appropriate PackageVersion
        """
        resp = requests.get("https://pypi.org/pypi/%s/json" % self.name)
        resp.raise_for_status()

        pv_and_cs = []

        releases = resp.json()["releases"]
        for release in releases:
            pv_and_cs.append(
                PackageVersion.objects.get_or_create(package=self, version=release)
            )

        return pv_and_cs


class PackageVersion(models.Model):
    package = models.ForeignKey("package", on_delete=models.CASCADE)
    version = models.CharField(max_length=120)
    setuppy = models.TextField()
    fetched = models.BooleanField(default=False)

    def __str__(self):
        return str(self.package) + "-" + self.version

    def fetch_sdist_url(self) -> Optional[str]:
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
            pass

        return None

    def fetch_setuppy(self) -> Optional[str]:
        """
        Fetches and saves and returns the sdist's setup.py, if it can be found
        """

        # TODO Fewer hacks, fewer assumptions, more modularity

        sdist_url = self.fetch_sdist_url()

        if sdist_url is None:
            return None

        resp = requests.get(sdist_url)
        resp.raise_for_status()

        setuppy = sdist.extract_setuppy(resp.content, self.package.name, self.version)

        self.setuppy = setuppy

        if setuppy:
            self.fetched = True

        self.save()

        return setuppy

    def parse_dependencies(self) -> Iterable["Dependency"]:
        install_requires = parser.parse_install_requires(self.setuppy)
        dependencies = []
        for spec in install_requires:
            dependency_name = parser.parse_dependency_name(spec)
            package, _ = Package.objects.get_or_create(name=dependency_name)
            dependency, _ = Dependency.objects.get_or_create(
                package_version=self, package=package
            )  # TODO Think about behaviour when someone has multiple requirements with duplicate package names!
            dependency.specification = spec
            dependency.save()
            dependencies.append(dependency)
        return dependencies


class Dependency(models.Model):
    """
    "Version 2 of Package Foo depends on Package Bar with some qualifiers"
    """

    class Meta:
        verbose_name_plural = "Dependencies"

    package_version = models.ForeignKey("PackageVersion", on_delete=models.CASCADE)
    package = models.ForeignKey("Package", on_delete=models.CASCADE)
    specification = models.CharField(max_length=1000)

    def __str__(self):
        return "Dependency(%s -> %s (%s))" % (
            self.package_version,
            self.package,
            self.specification,
        )
