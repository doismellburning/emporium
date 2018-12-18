from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .forms import PackageForm
from .models import Dependency, Package, PackageVersion


class PackageListView(ListView):
    model = Package

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_package_form"] = PackageForm()
        return context


class PackageDetailView(DetailView):
    model = Package
    slug_url_kwarg = "name"

    def get_slug_field(self):
        return "name"


class AddPackageView(CreateView):
    model = Package
    form_class = PackageForm
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
    http_method_names = ["post"]

    def get_object(self):
        return self.get_queryset().get(
            package__name=self.kwargs["name"], version=self.kwargs["version"]
        )

    def post(self, request, *args, **kwargs):
        pv = self.get_object()
        pv.parse_dependencies()
        return redirect(reverse_lazy("packages"))


class DependencyDotData(TemplateView):
    template_name = "emporium/dependency_dot_data.dot"
    # content_type = "text/vnd.graphviz"
    content_type = "text/plain"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "dependencies"
        ] = (
            Dependency.objects.all()
        )  # TODO: Crude, doesn't unique by package or limit to latest PV
        # PackageVersion.objects.order_by("-version").distinct("version")
        return context
