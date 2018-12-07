from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .models import Package


class PackageListView(ListView):
    model = Package


class AddPackageView(CreateView):
    model = Package
    fields = ["name"]
    success_url = reverse_lazy("packages")


class FetchLatestPackageVersionView(View, SingleObjectMixin):
    model = Package
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        package.fetch_latest_version()
        return redirect(reverse_lazy("packages"))
