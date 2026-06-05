"""DRF serializers exposing the domain models over JSON."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from crm.models import Customer, Lead, SalesOrder, SalesOrderLine
from erp.models import Product, Category, Supplier
from wms.models import Warehouse, InventoryItem

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role", "is_active"]


class CustomerSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "name", "company", "email", "phone", "address", "is_active", "total_orders", "created_at"]


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ["id", "name", "email", "phone", "source", "status", "estimated_value", "assigned_to"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "sku", "name", "category", "category_name", "supplier", "unit_price", "cost_price", "is_active"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class SalesOrderLineSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrderLine
        fields = ["id", "product", "quantity", "unit_price", "line_total"]


class SalesOrderSerializer(serializers.ModelSerializer):
    lines = SalesOrderLineSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = SalesOrder
        fields = ["id", "reference", "customer", "customer_name", "status", "order_date", "lines", "total"]


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name", "code", "location", "is_active"]


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ["id", "warehouse", "warehouse_name", "product", "product_name", "quantity", "reorder_level", "needs_reorder"]
