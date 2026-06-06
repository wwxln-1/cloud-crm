"""Inject per-role navigation flags so templates hide inaccessible links."""
from accounts import roles


def navigation(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"nav": {}}
    return {
        "nav": {
            "crm": user.in_roles(roles.CRM_VIEW),
            "erp": user.in_roles(roles.ERP_VIEW),
            "products": user.in_roles(roles.PRODUCT_VIEW),
            "wms": user.in_roles(roles.WMS_VIEW),
            "users": user.in_roles(roles.USERS_VIEW),
            "admin_panel": user.is_admin_role,
        }
    }
