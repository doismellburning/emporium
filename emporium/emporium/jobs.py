import django_rq

from .models import Package, PackageVersion


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
