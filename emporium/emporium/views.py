import django_rq
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .forms import PackageForm
from .jobs import (
    fetch_all_versions,
    fetch_and_create_recent_packages,
    fetch_latest_version,
    fetch_setuppy,
    parse_dependencies,
)
from .models import Dependency, Package, PackageVersion


class IndexView(TemplateView):
    template_name = "emporium/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["package_count"] = Package.objects.count()
        context["packageversion_count"] = PackageVersion.objects.count()
        context["dependency_count"] = Dependency.objects.count()
        return context


class PackageListView(ListView):
    model = Package
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_package_form"] = PackageForm()
        context["package_count"] = Package.objects.count()
        context["packageversion_count"] = PackageVersion.objects.count()
        context["dependency_count"] = Dependency.objects.count()
        return context


class PackageDetailView(DetailView):
    model = Package
    slug_url_kwarg = "name"

    def get_slug_field(self):
        return "name"


class AddPackageView(LoginRequiredMixin, CreateView):
    model = Package
    form_class = PackageForm
    success_url = reverse_lazy("packages")

    def form_valid(self, form):
        response = super().form_valid(form)
        django_rq.enqueue(fetch_latest_version, self.object.name)
        return response


class FetchAllPackageVersionsView(LoginRequiredMixin, View, SingleObjectMixin):
    model = Package
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        django_rq.enqueue(fetch_all_versions, package.name)
        return redirect(self.get_object().get_absolute_url())


class FetchLatestPackageVersionView(LoginRequiredMixin, View, SingleObjectMixin):
    model = Package
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        django_rq.enqueue(fetch_latest_version, package.name)
        return redirect(self.get_object().get_absolute_url())


class FetchLatestPackageVersionsView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        for package in Package.objects.all():
            django_rq.enqueue(fetch_latest_version, package.name)
        return redirect(reverse_lazy("packages"))


class FetchPyPIRecentUpdatesView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        django_rq.enqueue(fetch_and_create_recent_packages)
        return redirect(reverse_lazy("packages"))


class FetchSetuppyView(LoginRequiredMixin, View, SingleObjectMixin):
    model = PackageVersion
    http_method_names = ["post"]

    def get_object(self):
        return self.get_queryset().get(
            package__name=self.kwargs["name"], version=self.kwargs["version"]
        )

    def post(self, request, *args, **kwargs):
        pv = self.get_object()
        django_rq.enqueue(fetch_setuppy, pv.package.name, pv.version)
        return redirect(reverse_lazy("packages"))


class ParseSetuppyView(LoginRequiredMixin, View, SingleObjectMixin):
    model = PackageVersion
    http_method_names = ["post"]

    def get_object(self):
        return self.get_queryset().get(
            package__name=self.kwargs["name"], version=self.kwargs["version"]
        )

    def post(self, request, *args, **kwargs):
        pv = self.get_object()
        django_rq.enqueue(parse_dependencies, pv.package.name, pv.version)
        return redirect(reverse_lazy("packages"))


class DependencyDotData(ListView):
    template_name = "emporium/dependency_dot_data.dot"
    content_type = "text/plain"
    context_object_name = "dependencies"

    def get_queryset(self):
        # TODO: Doesn't limit to latest PV!
        return Dependency.objects.distinct(
            "package_version__package__name", "package__name"
        ).select_related("package_version__package", "package")


class DependencyDotGraph(DependencyDotData):
    template_name = "emporium/dependency_graph.html"
    content_type = "text/html"


class PackageVersionDependencyGraphView(DetailView):
    # TODO Sort better abstraction
    model = PackageVersion
    template_name = "emporium/dependency_graph.html"

    def get_object(self, queryset=None):
        return PackageVersion.objects.get(
            package__name=self.kwargs.get("name"), version=self.kwargs.get("version")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # TODO Better way that doesn't involve all the DB hits?
        dependencies = []
        packages_seen = set()
        pv_queue = [self.object]
        while len(pv_queue) > 0:
            # print("DEPS: %s || SEEN: %s || QUEUE: %s" % (dependencies, packages_seen, pv_queue))
            pv = pv_queue.pop()
            if pv is None:
                continue
            if pv.package.name in packages_seen:
                continue
            packages_seen.add(pv.package.name)
            deps = pv.dependency_set.all()
            pv_queue.extend([dep.package.get_latest_version() for dep in deps])
            dependencies.extend(deps)

        ctx["dependencies"] = dependencies
        return ctx
