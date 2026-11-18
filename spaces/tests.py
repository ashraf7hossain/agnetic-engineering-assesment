from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Space, Testimonial


class TestifyFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="secure-pass-123",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="secure-pass-123",
        )
        self.space = Space.objects.create(
            owner=self.owner,
            name="Acme",
            slug="acme",
            header_title="Share your love",
            message="Tell us what you think.",
            collect_ratings=True,
        )

    def test_register_and_login(self):
        res = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "email": "new@example.com",
                "password1": "secure-pass-123",
                "password2": "secure-pass-123",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbie").exists())

    def test_dashboard_requires_login(self):
        res = self.client.get(reverse("spaces:dashboard"))
        self.assertEqual(res.status_code, 302)

    def test_owner_can_create_space(self):
        self.client.login(username="owner", password="secure-pass-123")
        res = self.client.post(
            reverse("spaces:create"),
            {
                "name": "Beta",
                "slug": "beta",
                "logo_url": "",
                "header_title": "Hi",
                "message": "Msg",
                "collect_ratings": True,
                "theme": "light",
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Space.objects.filter(slug="beta", owner=self.owner).exists())

    def test_submit_creates_pending(self):
        res = self.client.post(
            reverse("spaces:collect_submit", kwargs={"slug": "acme"}),
            {
                "name": "Pat",
                "email": "pat@example.com",
                "body": "Great product!",
                "rating": "5",
                "consent": True,
            },
        )
        self.assertEqual(res.status_code, 302)
        t = Testimonial.objects.get(email="pat@example.com")
        self.assertEqual(t.status, Testimonial.Status.PENDING)
        self.assertEqual(t.rating, 5)

    def test_submit_requires_consent(self):
        res = self.client.post(
            reverse("spaces:collect_submit", kwargs={"slug": "acme"}),
            {
                "name": "Pat",
                "email": "pat@example.com",
                "body": "Nope",
                "rating": "4",
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Testimonial.objects.count(), 0)

    def test_htmx_submit_returns_thank_you(self):
        res = self.client.post(
            reverse("spaces:collect_submit", kwargs={"slug": "acme"}),
            {
                "name": "Pat",
                "email": "pat@example.com",
                "body": "Awesome",
                "rating": "5",
                "consent": True,
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Thank you", res.content)

    def test_wall_shows_only_approved(self):
        Testimonial.objects.create(
            space=self.space,
            name="A",
            email="a@example.com",
            body="Pending",
            consent=True,
            status=Testimonial.Status.PENDING,
        )
        Testimonial.objects.create(
            space=self.space,
            name="B",
            email="b@example.com",
            body="Approved love",
            consent=True,
            status=Testimonial.Status.APPROVED,
            rating=5,
        )
        res = self.client.get(reverse("spaces:wall", kwargs={"slug": "acme"}))
        self.assertContains(res, "Approved love")
        self.assertNotContains(res, "Pending")

    def test_non_owner_cannot_moderate(self):
        t = Testimonial.objects.create(
            space=self.space,
            name="A",
            email="a@example.com",
            body="Hi",
            consent=True,
        )
        self.client.login(username="other", password="secure-pass-123")
        res = self.client.post(
            reverse("spaces:approve", kwargs={"slug": "acme", "pk": t.pk})
        )
        self.assertEqual(res.status_code, 403)
        t.refresh_from_db()
        self.assertEqual(t.status, Testimonial.Status.PENDING)

    def test_owner_can_approve_via_htmx(self):
        t = Testimonial.objects.create(
            space=self.space,
            name="A",
            email="a@example.com",
            body="Hi",
            consent=True,
        )
        self.client.login(username="owner", password="secure-pass-123")
        res = self.client.post(
            reverse("spaces:approve", kwargs={"slug": "acme", "pk": t.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(res.status_code, 200)
        t.refresh_from_db()
        self.assertEqual(t.status, Testimonial.Status.APPROVED)
        self.assertContains(res, "Approved")
