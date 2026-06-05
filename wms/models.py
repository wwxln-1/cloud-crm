"""WMS domain: warehouses, inventory, stock movements and shipments."""
from django.db import models
from core.models import TimeStampedModel


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class InventoryItem(models.Model):
    """Current stock level of a product in a given warehouse."""

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory")
    product = models.ForeignKey("erp.Product", on_delete=models.CASCADE, related_name="inventory")
    quantity = models.IntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ("warehouse", "product")
        ordering = ["product__name"]

    def __str__(self) -> str:
        return f"{self.product} @ {self.warehouse}: {self.quantity}"

    @property
    def needs_reorder(self) -> bool:
        return self.quantity <= self.reorder_level


class StockMovement(TimeStampedModel):
    """Audit trail of incoming/outgoing stock — every change is recorded."""

    class Direction(models.TextChoices):
        IN = "IN", "Incoming"
        OUT = "OUT", "Outgoing"

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="movements")
    product = models.ForeignKey("erp.Product", on_delete=models.PROTECT, related_name="movements")
    direction = models.CharField(max_length=3, choices=Direction.choices)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_direction_display()} {self.quantity} {self.product}"


class Shipment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"

    reference = models.CharField(max_length=40, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="shipments")
    sales_order = models.ForeignKey("crm.SalesOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    carrier = models.CharField(max_length=120, blank=True)
    shipped_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.reference
