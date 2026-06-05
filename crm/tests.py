"""Unit + integration tests for the CRM module."""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Customer, SalesOrder, SalesOrderLine
from erp.models import Product

User = get_user_model()


class CustomerModelTests(TestCase):
    def test_total_orders_property(self):
        c = Customer.objects.create(name="Acme")
        self.assertEqual(c.total_orders, 0)
        SalesOrder.objects.create(reference="SO-1", customer=c)
        self.assertEqual(c.total_orders, 1)


class SalesOrderTotalTests(TestCase):
    def test_order_total_sums_lines(self):
        c = Customer.objects.create(name="Acme")
        p = Product.objects.create(sku="S1", name="Tee", unit_price=Decimal("10.00"))
        o = SalesOrder.objects.create(reference="SO-2", customer=c)
        SalesOrderLine.objects.create(order=o, product=p, quantity=3, unit_price=Decimal("10.00"))
        self.assertEqual(o.total, Decimal("30.00"))


class CustomerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="pw12345!")

    def test_list_requires_login(self):
        resp = self.client.get(reverse("crm:customer_list"))
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_authenticated_can_create_customer(self):
        self.client.login(username="u1", password="pw12345!")
        resp = self.client.post(reverse("crm:customer_create"),
                                {"name": "New Co", "company": "X", "email": "a@b.com",
                                 "phone": "", "address": "", "is_active": "on"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Customer.objects.filter(name="New Co").exists())
