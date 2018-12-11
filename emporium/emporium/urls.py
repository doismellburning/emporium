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
from django.urls import path

from .views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("packages/", PackageListView.as_view(), name="packages"),
    path("packages/add/", AddPackageView.as_view(), name="add-package"),
    path(
        "packages/<int:pk>/fetch-latest-version/",
        FetchLatestPackageVersionView.as_view(),
        name="fetch-latest-package-version",
    ),
    path("packages/<str:name>/", PackageDetailView.as_view(), name="package"),
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
]
