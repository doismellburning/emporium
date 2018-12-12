from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .models import Package, PackageVersion
from .parser import parse_install_requires


class PackageListView(ListView):
    model = Package

    def get_queryset(self):
        return super().get_queryset().order_by("name")


class PackageDetailView(DetailView):
    model = Package
    slug_url_kwarg = "name"

    def get_slug_field(self):
        return "name"


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


class FetchSetuppyView(View, SingleObjectMixin):
    model = PackageVersion
    http_method_names = ["post"]

    def get_object(self):
        return self.get_queryset().get(
            package__name=self.kwargs["name"], version=self.kwargs["version"]
        )

    def post(self, request, *args, **kwargs):
        pv = self.get_object()
        pv.fetch_setuppy()
        return redirect(reverse_lazy("packages"))


class ParseSetuppyView(View, SingleObjectMixin):
    model = PackageVersion
    http_method_names = ["get"]

    def get_object(self):
        return self.get_queryset().get(
            package__name=self.kwargs["name"], version=self.kwargs["version"]
        )

    def get(self, request, *args, **kwargs):
        pv = self.get_object()
        d = parse_install_requires(pv.setuppy)
        return HttpResponse(str(d))
