"""Shared abstract models reused across CRM, ERP and WMS apps."""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Adds created/updated audit columns to any model that inherits it."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True
