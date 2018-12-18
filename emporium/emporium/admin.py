from django.contrib import admin

from .models import Dependency, Package, PackageVersion

admin.site.register(Dependency)
admin.site.register(Package)
admin.site.register(PackageVersion)
