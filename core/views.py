"""Reusable, role-aware generic CRUD views.

Every module's list/create/update/delete view inherits from these, so we get
consistent styling, search, pagination and permission handling without
repeating boilerplate per model.
"""
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView


# --- Permission mixin -----------------------------------------------------
class RoleRequiredMixin(LoginRequiredMixin):
    """Restrict a view to a set of roles; shows a friendly page otherwise."""

    allowed_roles: set | None = None  # None => any authenticated user

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if self.allowed_roles and not request.user.in_roles(self.allowed_roles):
            return render(request, "403.html", status=403)
        return super().dispatch(request, *args, **kwargs)


# --- Auto-styled Bootstrap form ------------------------------------------
class StyledModelForm(forms.ModelForm):
    """Applies Bootstrap classes to every widget automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", "form-check-input")
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault("class", "form-select")
            elif isinstance(w, forms.Textarea):
                w.attrs.update({"class": "form-control", "rows": 3})
            else:
                w.attrs.setdefault("class", "form-control")


# --- Generic views --------------------------------------------------------
class BaseListView(RoleRequiredMixin, ListView):
    template_name = "crud/list.html"
    paginate_by = 12
    columns: list = []          # [{"label": "Name", "field": "name", "badge": bool}]
    search_fields: list = []
    title = ""
    icon = "bi-table"
    create_url = None
    edit_url = None
    delete_url = None
    detail_url = None
    write_roles: set | None = None

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q and self.search_fields:
            cond = Q()
            for f in self.search_fields:
                cond |= Q(**{f + "__icontains": q})
            qs = qs.filter(cond)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        can_write = bool(self.write_roles and self.request.user.in_roles(self.write_roles))
        ctx.update({
            "columns": self.columns,
            "title": self.title,
            "icon": self.icon,
            "create_url": self.create_url,
            "edit_url": self.edit_url,
            "delete_url": self.delete_url,
            "detail_url": self.detail_url,
            "can_write": can_write,
            "searchable": bool(self.search_fields),
            "q": self.request.GET.get("q", ""),
        })
        return ctx


class _FormMixin(RoleRequiredMixin):
    template_name = "crud/form.html"
    fields: list = []
    title = ""
    list_url = None

    def get_form_class(self):
        return modelform_factory(self.model, form=StyledModelForm, fields=self.fields)

    def get_success_url(self):
        return reverse_lazy(self.list_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title": self.title, "list_url": self.list_url})
        return ctx


class BaseCreateView(_FormMixin, CreateView):
    def form_valid(self, form):
        if hasattr(form.instance, "created_by_id"):
            form.instance.created_by = self.request.user
        return super().form_valid(form)


class BaseUpdateView(_FormMixin, UpdateView):
    pass


class BaseDeleteView(RoleRequiredMixin, DeleteView):
    template_name = "crud/confirm_delete.html"
    list_url = None
    title = "Delete"

    def get_success_url(self):
        return reverse_lazy(self.list_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"list_url": self.list_url, "title": self.title})
        return ctx


class BaseDetailView(RoleRequiredMixin, DetailView):
    template_name = "crud/detail.html"
    title = ""
    detail_rows: list = []      # [{"label": "...", "field": "..."}]
    list_url = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title": self.title, "detail_rows": self.detail_rows, "list_url": self.list_url})
        return ctx
