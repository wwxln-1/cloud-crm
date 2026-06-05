"""CRM frontend: Customers, Leads, Sales Orders — fully managed in the UI."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts import roles
from core.views import (BaseListView, BaseCreateView, BaseUpdateView,
                        BaseDeleteView, BaseDetailView, StyledModelForm)
from .models import Customer, Lead, SalesOrder, SalesOrderLine
from erp.models import Product


# ---- Customers ----
class CustomerList(BaseListView):
    model = Customer
    allowed_roles = roles.CRM_VIEW
    write_roles = roles.CRM_WRITE
    title = "Customers"; icon = "bi-people"
    search_fields = ["name", "company", "email", "phone"]
    columns = [
        {"label": "Name", "field": "name"},
        {"label": "Company", "field": "company"},
        {"label": "Email", "field": "email"},
        {"label": "Orders", "field": "total_orders"},
        {"label": "Status", "field": "is_active", "badge": True},
    ]
    create_url = "crm:customer_create"; edit_url = "crm:customer_update"
    delete_url = "crm:customer_delete"; detail_url = "crm:customer_detail"


class CustomerCreate(BaseCreateView):
    model = Customer; allowed_roles = roles.CRM_WRITE
    fields = ["name", "company", "email", "phone", "address", "is_active"]
    title = "New Customer"; list_url = "crm:customer_list"


class CustomerUpdate(BaseUpdateView):
    model = Customer; allowed_roles = roles.CRM_WRITE
    fields = ["name", "company", "email", "phone", "address", "is_active"]
    title = "Edit Customer"; list_url = "crm:customer_list"


class CustomerDelete(BaseDeleteView):
    model = Customer; allowed_roles = roles.CRM_WRITE; list_url = "crm:customer_list"


class CustomerDetail(BaseDetailView):
    model = Customer; allowed_roles = roles.CRM_VIEW
    title = "Customer"; list_url = "crm:customer_list"
    detail_rows = [
        {"label": "Company", "field": "company"}, {"label": "Email", "field": "email"},
        {"label": "Phone", "field": "phone"}, {"label": "Address", "field": "address"},
        {"label": "Total orders", "field": "total_orders"},
    ]


# ---- Leads ----
class LeadList(BaseListView):
    model = Lead; allowed_roles = roles.CRM_VIEW; write_roles = roles.CRM_WRITE
    title = "Leads"; icon = "bi-funnel"
    search_fields = ["name", "email", "source"]
    columns = [
        {"label": "Name", "field": "name"}, {"label": "Source", "field": "source"},
        {"label": "Status", "field": "status", "badge": True},
        {"label": "Est. value", "field": "estimated_value"},
    ]
    create_url = "crm:lead_create"; edit_url = "crm:lead_update"; delete_url = "crm:lead_delete"


class LeadCreate(BaseCreateView):
    model = Lead; allowed_roles = roles.CRM_WRITE
    fields = ["name", "email", "phone", "source", "status", "estimated_value", "assigned_to"]
    title = "New Lead"; list_url = "crm:lead_list"


class LeadUpdate(BaseUpdateView):
    model = Lead; allowed_roles = roles.CRM_WRITE
    fields = ["name", "email", "phone", "source", "status", "estimated_value", "assigned_to"]
    title = "Edit Lead"; list_url = "crm:lead_list"


class LeadDelete(BaseDeleteView):
    model = Lead; allowed_roles = roles.CRM_WRITE; list_url = "crm:lead_list"


# ---- Sales Orders ----
class OrderList(BaseListView):
    model = SalesOrder; allowed_roles = roles.CRM_VIEW; write_roles = roles.CRM_WRITE
    title = "Sales Orders"; icon = "bi-cart3"
    search_fields = ["reference", "customer__name"]
    columns = [
        {"label": "Reference", "field": "reference"},
        {"label": "Customer", "field": "customer.name"},
        {"label": "Status", "field": "status", "badge": True},
        {"label": "Date", "field": "order_date"},
        {"label": "Total", "field": "total"},
    ]
    create_url = "crm:order_create"; delete_url = "crm:order_delete"; detail_url = "crm:order_detail"

    def get_queryset(self):
        return super().get_queryset().select_related("customer").prefetch_related("lines")


class OrderCreate(BaseCreateView):
    model = SalesOrder; allowed_roles = roles.CRM_WRITE
    fields = ["reference", "customer", "status"]
    title = "New Sales Order"; list_url = "crm:order_list"

    def get_success_url(self):
        from django.urls import reverse
        return reverse("crm:order_detail", args=[self.object.pk])


class OrderDelete(BaseDeleteView):
    model = SalesOrder; allowed_roles = roles.CRM_WRITE; list_url = "crm:order_list"


class LineForm(StyledModelForm):
    class Meta:
        model = SalesOrderLine
        fields = ["product", "quantity", "unit_price"]


class OrderDetail(BaseDetailView):
    """Order detail with inline 'add line item' form."""
    model = SalesOrder; allowed_roles = roles.CRM_VIEW
    template_name = "crm/order_detail.html"
    title = "Sales Order"; list_url = "crm:order_list"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["line_form"] = LineForm()
        ctx["can_write"] = self.request.user.in_roles(roles.CRM_WRITE)
        return ctx


def add_order_line(request, pk):
    """Handle the inline add-line form on the order detail page."""
    order = get_object_or_404(SalesOrder, pk=pk)
    if not request.user.in_roles(roles.CRM_WRITE):
        return render(request, "403.html", status=403)
    if request.method == "POST":
        form = LineForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.order = order
            if not line.unit_price:
                line.unit_price = line.product.unit_price
            line.save()
            messages.success(request, "Line item added.")
    return redirect("crm:order_detail", pk=pk)
