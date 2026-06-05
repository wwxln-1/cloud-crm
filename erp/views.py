"""ERP frontend: Products, Categories, Suppliers, Purchase Orders, Employees."""
from accounts import roles
from core.views import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView
from .models import Product, Category, Supplier, PurchaseOrder, Employee


# ---- Products (all roles view; Admin/Manager write) ----
class ProductList(BaseListView):
    model = Product; allowed_roles = roles.PRODUCT_VIEW; write_roles = roles.PRODUCT_WRITE
    title = "Products"; icon = "bi-tags"
    search_fields = ["sku", "name"]
    columns = [
        {"label": "SKU", "field": "sku"}, {"label": "Name", "field": "name"},
        {"label": "Category", "field": "category.name"},
        {"label": "Price", "field": "unit_price"},
        {"label": "Active", "field": "is_active", "badge": True},
    ]
    create_url = "erp:product_create"; edit_url = "erp:product_update"; delete_url = "erp:product_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("category", "supplier")


class ProductCreate(BaseCreateView):
    model = Product; allowed_roles = roles.PRODUCT_WRITE
    fields = ["sku", "name", "category", "supplier", "unit_price", "cost_price", "is_active"]
    title = "New Product"; list_url = "erp:product_list"


class ProductUpdate(BaseUpdateView):
    model = Product; allowed_roles = roles.PRODUCT_WRITE
    fields = ["sku", "name", "category", "supplier", "unit_price", "cost_price", "is_active"]
    title = "Edit Product"; list_url = "erp:product_list"


class ProductDelete(BaseDeleteView):
    model = Product; allowed_roles = roles.PRODUCT_WRITE; list_url = "erp:product_list"


# ---- Categories ----
class CategoryList(BaseListView):
    model = Category; allowed_roles = roles.ERP_VIEW; write_roles = roles.ERP_WRITE
    title = "Categories"; icon = "bi-diagram-3"; search_fields = ["name"]
    columns = [{"label": "Name", "field": "name"}, {"label": "Description", "field": "description"}]
    create_url = "erp:category_create"; edit_url = "erp:category_update"; delete_url = "erp:category_delete"


class CategoryCreate(BaseCreateView):
    model = Category; allowed_roles = roles.ERP_WRITE
    fields = ["name", "description"]; title = "New Category"; list_url = "erp:category_list"


class CategoryUpdate(BaseUpdateView):
    model = Category; allowed_roles = roles.ERP_WRITE
    fields = ["name", "description"]; title = "Edit Category"; list_url = "erp:category_list"


class CategoryDelete(BaseDeleteView):
    model = Category; allowed_roles = roles.ERP_WRITE; list_url = "erp:category_list"


# ---- Suppliers ----
class SupplierList(BaseListView):
    model = Supplier; allowed_roles = roles.ERP_VIEW; write_roles = roles.ERP_WRITE
    title = "Suppliers"; icon = "bi-truck"; search_fields = ["name", "contact_person", "email"]
    columns = [
        {"label": "Name", "field": "name"}, {"label": "Contact", "field": "contact_person"},
        {"label": "Email", "field": "email"}, {"label": "Phone", "field": "phone"},
    ]
    create_url = "erp:supplier_create"; edit_url = "erp:supplier_update"; delete_url = "erp:supplier_delete"


class SupplierCreate(BaseCreateView):
    model = Supplier; allowed_roles = roles.ERP_WRITE
    fields = ["name", "contact_person", "email", "phone", "address"]
    title = "New Supplier"; list_url = "erp:supplier_list"


class SupplierUpdate(BaseUpdateView):
    model = Supplier; allowed_roles = roles.ERP_WRITE
    fields = ["name", "contact_person", "email", "phone", "address"]
    title = "Edit Supplier"; list_url = "erp:supplier_list"


class SupplierDelete(BaseDeleteView):
    model = Supplier; allowed_roles = roles.ERP_WRITE; list_url = "erp:supplier_list"


# ---- Purchase Orders ----
class PurchaseList(BaseListView):
    model = PurchaseOrder; allowed_roles = roles.ERP_VIEW; write_roles = roles.ERP_WRITE
    title = "Purchase Orders"; icon = "bi-receipt"; search_fields = ["reference", "supplier__name"]
    columns = [
        {"label": "Reference", "field": "reference"}, {"label": "Supplier", "field": "supplier.name"},
        {"label": "Status", "field": "status", "badge": True}, {"label": "Expected", "field": "expected_date"},
    ]
    create_url = "erp:purchase_create"; edit_url = "erp:purchase_update"; delete_url = "erp:purchase_delete"

    def get_queryset(self):
        return super().get_queryset().select_related("supplier")


class PurchaseCreate(BaseCreateView):
    model = PurchaseOrder; allowed_roles = roles.ERP_WRITE
    fields = ["reference", "supplier", "status", "expected_date"]
    title = "New Purchase Order"; list_url = "erp:purchase_list"


class PurchaseUpdate(BaseUpdateView):
    model = PurchaseOrder; allowed_roles = roles.ERP_WRITE
    fields = ["reference", "supplier", "status", "expected_date"]
    title = "Edit Purchase Order"; list_url = "erp:purchase_list"


class PurchaseDelete(BaseDeleteView):
    model = PurchaseOrder; allowed_roles = roles.ERP_WRITE; list_url = "erp:purchase_list"


# ---- Employees ----
class EmployeeList(BaseListView):
    model = Employee; allowed_roles = roles.ERP_VIEW; write_roles = roles.ERP_WRITE
    title = "Employees"; icon = "bi-person-badge"; search_fields = ["full_name", "position", "department"]
    columns = [
        {"label": "Name", "field": "full_name"}, {"label": "Position", "field": "position"},
        {"label": "Department", "field": "department"}, {"label": "Email", "field": "email"},
    ]
    create_url = "erp:employee_create"; edit_url = "erp:employee_update"; delete_url = "erp:employee_delete"


class EmployeeCreate(BaseCreateView):
    model = Employee; allowed_roles = roles.ERP_WRITE
    fields = ["full_name", "position", "department", "email", "hired_on"]
    title = "New Employee"; list_url = "erp:employee_list"


class EmployeeUpdate(BaseUpdateView):
    model = Employee; allowed_roles = roles.ERP_WRITE
    fields = ["full_name", "position", "department", "email", "hired_on"]
    title = "Edit Employee"; list_url = "erp:employee_list"


class EmployeeDelete(BaseDeleteView):
    model = Employee; allowed_roles = roles.ERP_WRITE; list_url = "erp:employee_list"
