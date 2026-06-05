"""User management — Admin only — and authentication views."""
from django import forms
from django.contrib.auth import get_user_model
from accounts import roles
from core.views import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView, StyledModelForm

User = get_user_model()


class UserList(BaseListView):
    model = User; allowed_roles = roles.USERS_VIEW; write_roles = roles.USERS_WRITE
    title = "Users"; icon = "bi-shield-lock"
    search_fields = ["username", "first_name", "last_name", "email"]
    columns = [
        {"label": "Username", "field": "username"}, {"label": "Name", "field": "get_full_name"},
        {"label": "Email", "field": "email"}, {"label": "Role", "field": "role", "badge": True},
        {"label": "Active", "field": "is_active", "badge": True},
    ]
    create_url = "accounts:user_create"; edit_url = "accounts:user_update"; delete_url = "accounts:user_delete"


class UserCreateForm(StyledModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "phone", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserCreate(BaseCreateView):
    model = User; allowed_roles = roles.USERS_WRITE
    title = "New User"; list_url = "accounts:user_list"

    def get_form_class(self):
        return UserCreateForm


class UserUpdate(BaseUpdateView):
    model = User; allowed_roles = roles.USERS_WRITE
    fields = ["username", "first_name", "last_name", "email", "role", "phone", "is_active"]
    title = "Edit User"; list_url = "accounts:user_list"


class UserDelete(BaseDeleteView):
    model = User; allowed_roles = roles.USERS_WRITE; list_url = "accounts:user_list"
