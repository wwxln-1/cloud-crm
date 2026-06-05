from django.contrib import admin
from .models import Warehouse, InventoryItem, StockMovement, Shipment

admin.site.register(Warehouse)
admin.site.register(StockMovement)
admin.site.register(Shipment)

@admin.register(InventoryItem)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "reorder_level", "needs_reorder")
    list_filter = ("warehouse",)
