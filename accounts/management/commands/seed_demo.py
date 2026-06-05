"""Populate the database with realistic demo data for screenshots / testing.

Usage:  python manage.py seed_demo
Idempotent-ish: safe to run on an empty DB. Creates users for each role.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crm.models import Customer, Lead, SalesOrder, SalesOrderLine
from erp.models import Category, Supplier, Product
from wms.models import Warehouse, InventoryItem

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for the CloudERP platform"

    def handle(self, *args, **options):
        # --- Users for every role (password printed for demo only) ---
        roles = [
            ("admin", User.Role.ADMIN, True),
            ("manager", User.Role.MANAGER, False),
            ("warehouse", User.Role.WAREHOUSE, False),
            ("sales", User.Role.SALES, False),
        ]
        for username, role, is_super in roles:
            u, created = User.objects.get_or_create(username=username, defaults={"role": role})
            u.role = role
            u.is_staff = is_super or role in {User.Role.ADMIN, User.Role.MANAGER}
            u.is_superuser = is_super
            u.set_password("ChangeMe123!")
            u.save()
        self.stdout.write(self.style.SUCCESS("Users: admin/manager/warehouse/sales (pwd: ChangeMe123!)"))

        # --- Catalogue ---
        cats = [Category.objects.get_or_create(name=n)[0] for n in ["Shirts", "Trousers", "Outerwear", "Accessories"]]
        sups = [Supplier.objects.get_or_create(name=n)[0] for n in ["TextilePro Ltd", "FabricWorld", "GarmentHub"]]
        products = []
        for i in range(1, 21):
            p, _ = Product.objects.get_or_create(
                sku=f"SKU-{i:04d}",
                defaults=dict(name=f"Product {i}", category=random.choice(cats),
                              supplier=random.choice(sups),
                              unit_price=Decimal(random.randint(10, 90)),
                              cost_price=Decimal(random.randint(5, 40))),
            )
            products.append(p)

        # --- Warehouses + inventory ---
        whs = [Warehouse.objects.get_or_create(code=c, defaults={"name": n, "location": loc})[0]
               for c, n, loc in [("WH-CEN", "Central DC", "Tashkent"),
                                 ("WH-RGN", "Regional Hub", "Samarkand")]]
        for wh in whs:
            for p in products:
                InventoryItem.objects.get_or_create(
                    warehouse=wh, product=p,
                    defaults={"quantity": random.randint(0, 200), "reorder_level": 20})

        # --- Customers + leads + orders ---
        customers = []
        for i in range(1, 16):
            c, _ = Customer.objects.get_or_create(
                name=f"Customer {i}",
                defaults=dict(company=f"Retailer {i} LLC", email=f"customer{i}@example.com",
                              phone=f"+99890{random.randint(1000000,9999999)}"))
            customers.append(c)
        for i in range(1, 9):
            Lead.objects.get_or_create(name=f"Lead {i}",
                defaults={"status": random.choice(list(Lead.Status.values)),
                          "estimated_value": Decimal(random.randint(500, 9000))})
        for i in range(1, 21):
            order, created = SalesOrder.objects.get_or_create(
                reference=f"SO-{i:05d}",
                defaults=dict(customer=random.choice(customers),
                              status=random.choice(list(SalesOrder.Status.values))))
            if created:
                for _ in range(random.randint(1, 4)):
                    p = random.choice(products)
                    SalesOrderLine.objects.create(order=order, product=p,
                        quantity=random.randint(1, 6), unit_price=p.unit_price)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Customer.objects.count()} customers, {Product.objects.count()} products, "
            f"{SalesOrder.objects.count()} orders, {Warehouse.objects.count()} warehouses."))
