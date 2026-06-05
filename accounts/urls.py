from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("users/", views.UserList.as_view(), name="user_list"),
    path("users/new/", views.UserCreate.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", views.UserUpdate.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", views.UserDelete.as_view(), name="user_delete"),
]
