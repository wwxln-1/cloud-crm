"""Single source of truth for which roles can access which modules.

Used by both the navigation (to hide what a user cannot use) and the views
(to enforce access). Keeping it in one place means a new role or permission
change is a one-line edit, not a hunt across the codebase.
"""

ADMIN = "ADMIN"
MANAGER = "MANAGER"
WAREHOUSE = "WAREHOUSE"
SALES = "SALES"

# Who may VIEW each module
CRM_VIEW = {ADMIN, MANAGER, SALES}
ERP_VIEW = {ADMIN, MANAGER}            # suppliers, purchasing, employees, categories
PRODUCT_VIEW = {ADMIN, MANAGER, SALES, WAREHOUSE}
WMS_VIEW = {ADMIN, MANAGER, WAREHOUSE}
USERS_VIEW = {ADMIN}
API_VIEW = {ADMIN, MANAGER}

# Who may WRITE (create/edit/delete) — drives whether buttons appear
CRM_WRITE = {ADMIN, MANAGER, SALES}
ERP_WRITE = {ADMIN, MANAGER}
PRODUCT_WRITE = {ADMIN, MANAGER}
WMS_WRITE = {ADMIN, MANAGER, WAREHOUSE}
USERS_WRITE = {ADMIN}
