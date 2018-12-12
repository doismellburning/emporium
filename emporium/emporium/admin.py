from django.contrib import admin

from .models import Package, PackageVersion

admin.site.register(Package)
admin.site.register(PackageVersion)
