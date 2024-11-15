"""emporium URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .views import (
    AddPackageView,
    DependencyDotData,
    DependencyDotGraph,
    FetchAllPackageVersionsView,
    FetchLatestPackageVersionsView,
    FetchLatestPackageVersionView,
    FetchPyPIRecentUpdatesView,
    FetchSetuppyView,
    IndexView,
    PackageDetailView,
    PackageListView,
    PackageSearchView,
    PackageVersionDependencyGraphView,
    ParseSetuppyView,
)


def cache_page_by_cookie(*args, **kwargs):
    return lambda x: cache_page(*args, **kwargs)(vary_on_cookie(x))


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("django-rq/", include("django_rq.urls")),
    path(
        "packages/",
        cache_page_by_cookie(60)(PackageListView.as_view()),
        name="packages",
    ),
    path("packages/search/", PackageSearchView.as_view(), name="search"),
    path("packages/add/", AddPackageView.as_view(), name="add-package"),
    path(
        "packages/fetch-latest-versions/",
        FetchLatestPackageVersionsView.as_view(),
        name="fetch-latest-package-versions",
    ),
    path(
        "packages/fetch-pypi-recent-updates/",
        FetchPyPIRecentUpdatesView.as_view(),
        name="fetch-pypi-recent-updates",
    ),
    path(
        "packages/<int:pk>/fetch-latest-version/",
        FetchLatestPackageVersionView.as_view(),
        name="fetch-latest-package-version",
    ),
    path(
        "packages/<int:pk>/fetch-all-versions/",
        FetchAllPackageVersionsView.as_view(),
        name="fetch-all-package-versions",
    ),
    path(
        "packages/<str:name>/",
        cache_page_by_cookie(60)(PackageDetailView.as_view()),
        name="package",
    ),
    path(
        "packages/<str:name>/<str:version>/fetch-setuppy/",
        FetchSetuppyView.as_view(),
        name="fetch-setuppy",
    ),
    path(
        "packages/<str:name>/<str:version>/parse/",
        ParseSetuppyView.as_view(),
        name="parse-setuppy",
    ),
    path(
        "packages/<str:name>/<str:version>/graph/",
        cache_page_by_cookie(60)(PackageVersionDependencyGraphView.as_view()),
        name="package-version-dependency-graph",
    ),
    path("dot/", cache_page_by_cookie(60)(DependencyDotData.as_view()), name="dot"),
    path(
        "graph/", cache_page_by_cookie(60)(DependencyDotGraph.as_view()), name="graph"
    ),
]
