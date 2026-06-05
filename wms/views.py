"""WMS frontend: Warehouses, Inventory, Stock Movements, Shipments."""
from accounts import roles
from core.views import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView


class WarehouseList(BaseListView):
    model = None; allowed_roles = roles.WMS_VIEW; write_roles = roles.WMS_WRITE
    title = "Warehouses"; icon = "bi-buildings"; search_fields = ["name", "code", "location"]
    columns = [
        {"label": "Code", "field": "code"}, {"label": "Name", "field": "name"},
        {"label": "Location", "field": "location"}, {"label": "Active", "field": "is_active", "badge": True},
    ]
    create_url = "wms:warehouse_create"; edit_url = "wms:warehouse_update"; delete_url = "wms:warehouse_delete"


class InventoryList(BaseListView):
    allowed_roles = roles.WMS_VIEW; write_roles = roles.WMS_WRITE
    title = "Inventory"; icon = "bi-boxes"; search_fields = ["product__name", "product__sku"]
    columns = [
        {"label": "Product", "field": "product.name"}, {"label": "Warehouse", "field": "warehouse.name"},
        {"label": "Qty", "field": "quantity"}, {"label": "Reorder at", "field": "reorder_level"},
        {"label": "Reorder?", "field": "needs_reorder", "badge": True},
    ]
    create_url = "wms:inventory_create"; edit_url = "wms:inventory_update"; delete_url = "wms:inventory_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("product", "warehouse")


class MovementList(BaseListView):
    allowed_roles = roles.WMS_VIEW; write_roles = roles.WMS_WRITE
    title = "Stock Movements"; icon = "bi-arrow-left-right"; search_fields = ["product__name", "reference"]
    columns = [
        {"label": "Product", "field": "product.name"}, {"label": "Warehouse", "field": "warehouse.name"},
        {"label": "Direction", "field": "direction", "badge": True}, {"label": "Qty", "field": "quantity"},
        {"label": "Reference", "field": "reference"},
    ]
    create_url = "wms:movement_create"; edit_url = "wms:movement_update"; delete_url = "wms:movement_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("product", "warehouse")


class ShipmentList(BaseListView):
    allowed_roles = roles.WMS_VIEW; write_roles = roles.WMS_WRITE
    title = "Shipments"; icon = "bi-send"; search_fields = ["reference", "carrier"]
    columns = [
        {"label": "Reference", "field": "reference"}, {"label": "Warehouse", "field": "warehouse.name"},
        {"label": "Status", "field": "status", "badge": True}, {"label": "Carrier", "field": "carrier"},
        {"label": "Shipped", "field": "shipped_on"},
    ]
    create_url = "wms:shipment_create"; edit_url = "wms:shipment_update"; delete_url = "wms:shipment_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("warehouse")


# bind models (avoids importing at class-def order issues)
from .models import Warehouse, InventoryItem, StockMovement, Shipment  # noqa: E402
WarehouseList.model = Warehouse
InventoryList.model = InventoryItem
MovementList.model = StockMovement
ShipmentList.model = Shipment


class WarehouseCreate(BaseCreateView):
    model = Warehouse; allowed_roles = roles.WMS_WRITE
    fields = ["name", "code", "location", "is_active"]; title = "New Warehouse"; list_url = "wms:warehouse_list"


class WarehouseUpdate(BaseUpdateView):
    model = Warehouse; allowed_roles = roles.WMS_WRITE
    fields = ["name", "code", "location", "is_active"]; title = "Edit Warehouse"; list_url = "wms:warehouse_list"


class WarehouseDelete(BaseDeleteView):
    model = Warehouse; allowed_roles = roles.WMS_WRITE; list_url = "wms:warehouse_list"


class InventoryCreate(BaseCreateView):
    model = InventoryItem; allowed_roles = roles.WMS_WRITE
    fields = ["warehouse", "product", "quantity", "reorder_level"]; title = "New Inventory Item"; list_url = "wms:inventory_list"


class InventoryUpdate(BaseUpdateView):
    model = InventoryItem; allowed_roles = roles.WMS_WRITE
    fields = ["warehouse", "product", "quantity", "reorder_level"]; title = "Edit Inventory Item"; list_url = "wms:inventory_list"


class InventoryDelete(BaseDeleteView):
    model = InventoryItem; allowed_roles = roles.WMS_WRITE; list_url = "wms:inventory_list"


class MovementCreate(BaseCreateView):
    model = StockMovement; allowed_roles = roles.WMS_WRITE
    fields = ["warehouse", "product", "direction", "quantity", "reference"]; title = "New Stock Movement"; list_url = "wms:movement_list"


class MovementUpdate(BaseUpdateView):
    model = StockMovement; allowed_roles = roles.WMS_WRITE
    fields = ["warehouse", "product", "direction", "quantity", "reference"]; title = "Edit Stock Movement"; list_url = "wms:movement_list"


class MovementDelete(BaseDeleteView):
    model = StockMovement; allowed_roles = roles.WMS_WRITE; list_url = "wms:movement_list"


class ShipmentCreate(BaseCreateView):
    model = Shipment; allowed_roles = roles.WMS_WRITE
    fields = ["reference", "warehouse", "sales_order", "status", "carrier", "shipped_on"]; title = "New Shipment"; list_url = "wms:shipment_list"


class ShipmentUpdate(BaseUpdateView):
    model = Shipment; allowed_roles = roles.WMS_WRITE
    fields = ["reference", "warehouse", "sales_order", "status", "carrier", "shipped_on"]; title = "Edit Shipment"; list_url = "wms:shipment_list"


class ShipmentDelete(BaseDeleteView):
    model = Shipment; allowed_roles = roles.WMS_WRITE; list_url = "wms:shipment_list"
