"""Root URL configuration for the CloudERP CRM WMS Platform."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("crm/", include("crm.urls")),
    path("erp/", include("erp.urls")),
    path("wms/", include("wms.urls")),
    path("", include("dashboard.urls")),
]
