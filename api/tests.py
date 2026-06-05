"""API tests: authentication, permissions and CRUD."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from crm.models import Customer

User = get_user_model()


class ApiAuthTests(TestCase):
    def setUp(self):
        self.sales = User.objects.create_user("sales", password="pw12345!", role=User.Role.SALES)
        self.manager = User.objects.create_user("mgr", password="pw12345!", role=User.Role.MANAGER)
        Customer.objects.create(name="Existing")

    def test_anonymous_denied(self):
        resp = self.client.get("/api/customers/")
        self.assertIn(resp.status_code, (401, 403))

    def test_authenticated_can_list(self):
        self.client.login(username="sales", password="pw12345!")
        resp = self.client.get("/api/customers/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.json())  # pagination present

    def test_sales_cannot_create_customer(self):
        # IsManagerOrReadOnly: sales has read-only
        self.client.login(username="sales", password="pw12345!")
        resp = self.client.post("/api/customers/", {"name": "Blocked"})
        self.assertEqual(resp.status_code, 403)

    def test_manager_can_create_customer(self):
        self.client.login(username="mgr", password="pw12345!")
        resp = self.client.post("/api/customers/", {"name": "Allowed"})
        self.assertEqual(resp.status_code, 201)

    def test_search_filter(self):
        self.client.login(username="sales", password="pw12345!")
        resp = self.client.get("/api/customers/?search=Existing")
        self.assertEqual(resp.json()["count"], 1)


class HealthCheckTests(TestCase):
    def test_health_ok(self):
        resp = self.client.get(reverse("dashboard:health"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")
