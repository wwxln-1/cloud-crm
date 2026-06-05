"""DRF ViewSets: CRUD + filtering + search + pagination for all modules."""
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsManagerOrReadOnly, IsAdminRole
from crm.models import Customer, SalesOrder
from erp.models import Product
from wms.models import Warehouse, InventoryItem
from .serializers import (
    CustomerSerializer, SalesOrderSerializer, ProductSerializer,
    WarehouseSerializer, InventorySerializer, UserSerializer,
)

User = get_user_model()


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsManagerOrReadOnly]
    filterset_fields = ["is_active", "company"]
    search_fields = ["name", "company", "email", "phone"]
    ordering_fields = ["name", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.select_related("customer").prefetch_related("lines")
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "customer"]
    search_fields = ["reference", "customer__name"]
    ordering_fields = ["order_date", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "supplier")
    serializer_class = ProductSerializer
    permission_classes = [IsManagerOrReadOnly]
    filterset_fields = ["category", "supplier", "is_active"]
    search_fields = ["sku", "name"]
    ordering_fields = ["name", "unit_price"]


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsManagerOrReadOnly]
    search_fields = ["name", "code", "location"]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related("product", "warehouse")
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["warehouse", "product"]
    search_fields = ["product__name", "product__sku"]
    ordering_fields = ["quantity"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["username", "email", "first_name", "last_name"]
    filterset_fields = ["role", "is_active"]
