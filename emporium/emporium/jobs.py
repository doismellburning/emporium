import django_rq

from .feed import fetch_pypi_recent_updates
from .models import Package, PackageVersion


def fetch_all_versions(package_name):
    package = Package.objects.get(name=package_name)
    pv_and_cs = package.fetch_all_versions()

    for (pv, created) in pv_and_cs:
        if created:
            django_rq.enqueue("emporium.jobs.fetch_setuppy", package_name, pv.version)


def fetch_latest_version(package_name):
    package = Package.objects.get(name=package_name)
    (pv, created) = package.fetch_latest_version()

    if created:
        django_rq.enqueue("emporium.jobs.fetch_setuppy", package_name, pv.version)


def fetch_setuppy(package_name, package_version):
    pv = PackageVersion.objects.get(package__name=package_name, version=package_version)
    pv.fetch_setuppy()

    django_rq.enqueue("emporium.jobs.parse_dependencies", package_name, package_version)


def parse_dependencies(package_name, package_version):
    pv = PackageVersion.objects.get(package__name=package_name, version=package_version)
    dependencies = pv.parse_dependencies()

    for dependency in dependencies:
        django_rq.enqueue("emporium.jobs.fetch_latest_version", dependency.package.name)


def fetch_and_create_recent_packages():
    # TODO Cut down on useless work by comparing RSS version with what we have stored
    # For now, just assume we run this infrequently enough that it will be ok

    package_names = fetch_pypi_recent_updates()

    for package_name in package_names:
        Package.objects.get_or_create(name=package_name)
        django_rq.enqueue("emporium.jobs.fetch_latest_version", package_name)
