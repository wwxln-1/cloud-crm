from django.urls import path
from . import views

app_name = "crm"
urlpatterns = [
    # Customers
    path("customers/", views.CustomerList.as_view(), name="customer_list"),
    path("customers/new/", views.CustomerCreate.as_view(), name="customer_create"),
    path("customers/<int:pk>/", views.CustomerDetail.as_view(), name="customer_detail"),
    path("customers/<int:pk>/edit/", views.CustomerUpdate.as_view(), name="customer_update"),
    path("customers/<int:pk>/delete/", views.CustomerDelete.as_view(), name="customer_delete"),
    # Leads
    path("leads/", views.LeadList.as_view(), name="lead_list"),
    path("leads/new/", views.LeadCreate.as_view(), name="lead_create"),
    path("leads/<int:pk>/edit/", views.LeadUpdate.as_view(), name="lead_update"),
    path("leads/<int:pk>/delete/", views.LeadDelete.as_view(), name="lead_delete"),
    # Orders
    path("orders/", views.OrderList.as_view(), name="order_list"),
    path("orders/new/", views.OrderCreate.as_view(), name="order_create"),
    path("orders/<int:pk>/", views.OrderDetail.as_view(), name="order_detail"),
    path("orders/<int:pk>/add-line/", views.add_order_line, name="order_add_line"),
    path("orders/<int:pk>/delete/", views.OrderDelete.as_view(), name="order_delete"),
]
