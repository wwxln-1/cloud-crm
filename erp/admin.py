from django.contrib import admin
from .models import Category, Supplier, Product, Employee, PurchaseOrder

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Employee)
admin.site.register(PurchaseOrder)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "unit_price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name")
