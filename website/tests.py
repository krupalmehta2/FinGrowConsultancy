from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    BlogPost,
    ContactInquiry,
    GovernmentScheme,
    NewsletterSubscriber,
    Service,
    ServiceCategory,
)


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicContentAccessTests(TestCase):
    """Public marketing content must never depend on an existing session."""

    @classmethod
    def setUpTestData(cls):
        cls.category = ServiceCategory.objects.create(name="Advisory", slug="advisory")
        cls.service = Service.objects.create(
            title="Business advisory",
            slug="business-advisory",
            category=cls.category,
            short_description="Guidance for founders.",
        )
        cls.scheme = GovernmentScheme.objects.create(
            title="Growth scheme",
            slug="growth-scheme",
            short_description="Funding guidance.",
        )
        cls.post = BlogPost.objects.create(
            title="Planning guide",
            slug="planning-guide",
            short_description="A practical guide.",
            content="Content",
            author="FinGrow",
        )
        cls.user = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="safe-test-password",
        )

    def public_urls(self):
        return [
            reverse("home"),
            reverse("about"),
            reverse("process"),
            reverse("services"),
            reverse("service_category", args=[self.category.slug]),
            reverse("service_detail", args=[self.service.slug]),
            reverse("government_schemes"),
            reverse("government_scheme_detail", args=[self.scheme.slug]),
            reverse("blog"),
            reverse("blog_detail", args=[self.post.slug]),
            reverse("contact"),
            reverse("privacy_policy"),
            reverse("terms"),
            reverse("refund_policy"),
        ]

    def test_fresh_session_can_open_every_public_page(self):
        for url in self.public_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn(reverse("login"), response.get("Location", ""))

    def test_authenticated_user_can_open_every_public_page(self):
        self.client.force_login(self.user)
        for url in self.public_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous_contact_and_newsletter_forms_work(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Visitor",
                "phone": "9999999999",
                "email": "visitor@example.com",
                "subject": "Consultation",
                "message": "Please contact me.",
            },
        )
        self.assertRedirects(response, reverse("contact"))
        self.assertTrue(ContactInquiry.objects.filter(email="visitor@example.com").exists())

        response = self.client.post(
            reverse("newsletter_subscribe"),
            {"newsletter_email": "subscriber@example.com"},
            HTTP_REFERER=reverse("home"),
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(NewsletterSubscriber.objects.filter(email="subscriber@example.com").exists())

    def test_admin_and_staff_integrations_remain_protected(self):
        admin_response = self.client.get(reverse("admin:index"))
        self.assertEqual(admin_response.status_code, 302)
        self.assertIn(reverse("admin:login"), admin_response["Location"])

        integration_response = self.client.get(reverse("linkedin_connect"))
        self.assertEqual(integration_response.status_code, 302)
        self.assertIn(reverse("login"), integration_response["Location"])
