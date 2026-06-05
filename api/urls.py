"""API router — exposes /api/<resource>/ endpoints required by the brief."""
from rest_framework.routers import DefaultRouter
from . import views

app_name = "api"
router = DefaultRouter()
router.register("customers", views.CustomerViewSet)
router.register("orders", views.SalesOrderViewSet)
router.register("products", views.ProductViewSet)
router.register("warehouses", views.WarehouseViewSet)
router.register("inventory", views.InventoryViewSet)
router.register("users", views.UserViewSet)

urlpatterns = router.urls
