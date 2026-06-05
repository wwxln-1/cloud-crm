"""Role-aware dashboard + load-balancer health endpoint."""
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, DecimalField
from django.http import JsonResponse
from django.shortcuts import render

from accounts import roles
from crm.models import Customer, SalesOrder, Lead
from erp.models import Product
from wms.models import Warehouse, InventoryItem


@login_required
def home(request):
    user = request.user
    ctx = {"show_crm": user.in_roles(roles.CRM_VIEW), "show_wms": user.in_roles(roles.WMS_VIEW)}

    if ctx["show_crm"]:
        orders = SalesOrder.objects.prefetch_related("lines")
        ctx["total_customers"] = Customer.objects.count()
        ctx["total_orders"] = orders.count()
        ctx["revenue"] = sum((o.total for o in orders), start=0)
        ctx["open_leads"] = Lead.objects.exclude(status__in=["WON", "LOST"]).count()
        # orders grouped by status for the doughnut chart
        status_counts = SalesOrder.objects.values("status").annotate(n=Count("id"))
        ctx["status_labels"] = [s["status"] for s in status_counts]
        ctx["status_values"] = [s["n"] for s in status_counts]

    if ctx["show_wms"]:
        ctx["total_warehouses"] = Warehouse.objects.count()
        ctx["low_stock"] = InventoryItem.objects.filter(quantity__lte=F("reorder_level")).count()
        # stock per warehouse for the bar chart
        per_wh = (InventoryItem.objects.values("warehouse__name")
                  .annotate(qty=Sum("quantity")).order_by("warehouse__name"))
        ctx["wh_labels"] = [w["warehouse__name"] for w in per_wh]
        ctx["wh_values"] = [w["qty"] or 0 for w in per_wh]

    ctx["total_products"] = Product.objects.count()
    ctx["recent_orders"] = (SalesOrder.objects.select_related("customer")
                            .order_by("-created_at")[:6]) if ctx["show_crm"] else []
    return render(request, "dashboard/home.html", ctx)


def health(request):
    """Health check for the AWS load balancer / Auto Scaling Group."""
    return JsonResponse({"status": "ok"})
