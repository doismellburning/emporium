from django.views.generic.list import ListView

from .models import Package


class PackageListView(ListView):
    model = Package
