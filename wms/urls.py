from django.urls import path
from . import views

app_name = "wms"


def _crud(prefix, name, v):
    return [
        path(f"{prefix}/", v["list"].as_view(), name=f"{name}_list"),
        path(f"{prefix}/new/", v["create"].as_view(), name=f"{name}_create"),
        path(f"{prefix}/<int:pk>/edit/", v["update"].as_view(), name=f"{name}_update"),
        path(f"{prefix}/<int:pk>/delete/", v["delete"].as_view(), name=f"{name}_delete"),
    ]


urlpatterns = (
    _crud("warehouses", "warehouse", {"list": views.WarehouseList, "create": views.WarehouseCreate,
                                       "update": views.WarehouseUpdate, "delete": views.WarehouseDelete})
    + _crud("inventory", "inventory", {"list": views.InventoryList, "create": views.InventoryCreate,
                                        "update": views.InventoryUpdate, "delete": views.InventoryDelete})
    + _crud("movements", "movement", {"list": views.MovementList, "create": views.MovementCreate,
                                       "update": views.MovementUpdate, "delete": views.MovementDelete})
    + _crud("shipments", "shipment", {"list": views.ShipmentList, "create": views.ShipmentCreate,
                                       "update": views.ShipmentUpdate, "delete": views.ShipmentDelete})
)
