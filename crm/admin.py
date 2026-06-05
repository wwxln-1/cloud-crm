from django.contrib import admin
from .models import Customer, Lead, SalesOrder, SalesOrderLine

class LineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "is_active")
    search_fields = ("name", "company", "email")

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "estimated_value", "assigned_to")
    list_filter = ("status",)

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "status", "order_date")
    list_filter = ("status",)
    inlines = [LineInline]
