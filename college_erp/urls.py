"""
URL configuration for college_erp project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        include("students.urls"),
    ),

    path(
        "accounts/",
        include("accounts.urls"),
    ),

    path(
        "finance/",
        include("finance.urls"),
    ),

    path(
        "graduation/",
        include("graduation.urls"),
    ),

    path(
        "system/",
        include("system.urls"),
    ),

    path(
        "communication/",
        include("communication.urls"),
    ),

]


# =========================================================
# USER-UPLOADED MEDIA FILES
# =========================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )