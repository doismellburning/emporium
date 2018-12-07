from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .models import Package


class PackageListView(ListView):
    model = Package


class AddPackageView(CreateView):
    model = Package
    fields = ["name"]
    success_url = reverse_lazy("packages")
