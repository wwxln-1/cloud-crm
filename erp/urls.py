from django.urls import path
from . import views

app_name = "erp"


def _crud(prefix, name, v):
    return [
        path(f"{prefix}/", v["list"].as_view(), name=f"{name}_list"),
        path(f"{prefix}/new/", v["create"].as_view(), name=f"{name}_create"),
        path(f"{prefix}/<int:pk>/edit/", v["update"].as_view(), name=f"{name}_update"),
        path(f"{prefix}/<int:pk>/delete/", v["delete"].as_view(), name=f"{name}_delete"),
    ]


urlpatterns = (
    _crud("products", "product", {"list": views.ProductList, "create": views.ProductCreate,
                                   "update": views.ProductUpdate, "delete": views.ProductDelete})
    + _crud("categories", "category", {"list": views.CategoryList, "create": views.CategoryCreate,
                                        "update": views.CategoryUpdate, "delete": views.CategoryDelete})
    + _crud("suppliers", "supplier", {"list": views.SupplierList, "create": views.SupplierCreate,
                                       "update": views.SupplierUpdate, "delete": views.SupplierDelete})
    + _crud("purchase-orders", "purchase", {"list": views.PurchaseList, "create": views.PurchaseCreate,
                                             "update": views.PurchaseUpdate, "delete": views.PurchaseDelete})
    + _crud("employees", "employee", {"list": views.EmployeeList, "create": views.EmployeeCreate,
                                       "update": views.EmployeeUpdate, "delete": views.EmployeeDelete})
)
