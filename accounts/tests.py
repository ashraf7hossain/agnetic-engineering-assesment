from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountsTests(TestCase):
    def test_login_page_renders(self):
        res = self.client.get(reverse("accounts:login"))
        self.assertEqual(res.status_code, 200)

    def test_password_reset_page_renders(self):
        res = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(res.status_code, 200)

    def test_login_success(self):
        User.objects.create_user(username="u1", password="secure-pass-123")
        res = self.client.post(
            reverse("accounts:login"),
            {"username": "u1", "password": "secure-pass-123"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("spaces:dashboard"))
