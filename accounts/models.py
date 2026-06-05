"""Custom user model with Role Based Access Control (RBAC)."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        MANAGER = "MANAGER", "Manager"
        WAREHOUSE = "WAREHOUSE", "Warehouse Staff"
        SALES = "SALES", "Sales Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SALES)
    phone = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def in_roles(self, allowed) -> bool:
        """True if this user's role is in `allowed` (superuser always passes)."""
        return self.is_superuser or self.role in allowed

    @property
    def is_admin_role(self) -> bool:
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_manager_role(self) -> bool:
        return self.is_superuser or self.role in {self.Role.ADMIN, self.Role.MANAGER}
