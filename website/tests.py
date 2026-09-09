from django.contrib.auth.models import User
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.conf import settings
from django.test import Client, TestCase, override_settings
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

    def test_legacy_scheme_urls_redirect_to_the_canonical_incubation_routes(self):
        response = self.client.get(reverse("government_schemes"), follow=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], reverse("incubation_schemes"))
        response = self.client.get(reverse("government_scheme_detail", args=[self.scheme.slug]), follow=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], reverse("incubation_scheme_detail", args=[self.scheme.slug]))
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


@override_settings(
    SECURE_SSL_REDIRECT=False,
    RESEND_API_KEY="test-key",
    INQUIRY_NOTIFICATION_FROM="FinGrow <notifications@example.com>",
    INQUIRY_NOTIFICATION_TO="fingrowconsultancyservices@gmail.com",
)
class InquiryNotificationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = ServiceCategory.objects.create(name="Advisory", slug="advisory-notify")
        self.service = Service.objects.create(title="Business advisory", slug="business-advisory-notify", category=self.category, short_description="Guidance")
        self.scheme = GovernmentScheme.objects.create(title="Growth scheme", slug="growth-scheme-notify", short_description="Funding guidance")
        self.post = BlogPost.objects.create(title="Planning guide", slug="planning-guide-notify", short_description="Guide", content="Content", author="FinGrow")
        self.data = {"name": "Visitor", "phone": "9999999999", "email": "visitor@example.com", "subject": "Consultation", "message": "Please contact me."}
        self.user = User.objects.create_user(username="inquiry-user", email="inquiry@example.com", password="safe-test-password")

    def _post(self, url, **headers):
        return self.client.post(url, self.data, **headers)

    @patch("website.views.send_inquiry_notification", return_value=True)
    def test_general_service_and_incubation_inquiries_save_and_notify(self, notify):
        self.client.force_login(self.user)
        cases = [
            (reverse("contact"), "General", "Contact Us"),
            (reverse("service_detail", args=[self.service.slug]), "Service", self.service.title),
            (reverse("incubation_scheme_detail", args=[self.scheme.slug]), "Incubation Scheme", self.scheme.title),
        ]
        for url, page_type, page_title in cases:
            cache.clear()
            with self.subTest(page_type=page_type):
                response = self._post(url)
                self.assertEqual(response.status_code, 302)
                inquiry = ContactInquiry.objects.filter(page_type=page_type).latest("created_at")
                self.assertEqual(inquiry.page_title, page_title)
        self.assertEqual(notify.call_count, 3)

    @patch("website.views.send_inquiry_notification")
    def test_invalid_inquiry_does_not_notify(self, notify):
        response = self.client.post(reverse("contact"), {**self.data, "email": "not-an-email"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(ContactInquiry.objects.count(), 0)
        notify.assert_not_called()

    @patch("website.views.send_inquiry_notification", return_value=False)
    def test_notification_failure_keeps_saved_inquiry_and_ajax_succeeds(self, notify):
        response = self._post(reverse("contact"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(response.json()["notification_sent"])
        self.assertEqual(ContactInquiry.objects.count(), 1)
        notify.assert_called_once()

    @patch("website.notifications.urlopen")
    def test_resend_notification_uses_recipient_and_reply_to(self, mocked_urlopen):
        response = MagicMock()
        response.status = 202
        mocked_urlopen.return_value.__enter__.return_value = response
        from .notifications import send_inquiry_notification

        inquiry = ContactInquiry.objects.create(**self.data, page_type="Service", page_title=self.service.title, current_url="https://example.com/services/business-advisory-notify/")
        self.assertTrue(send_inquiry_notification(inquiry))
        request = mocked_urlopen.call_args.args[0]
        import json
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["to"], ["fingrowconsultancyservices@gmail.com"])
        self.assertEqual(payload["reply_to"], "visitor@example.com")
        self.assertEqual(payload["from"], "FinGrow <notifications@example.com>")
        self.assertIn("NEW LEAD", payload["subject"])
        self.assertIn("Page Title: Business advisory", payload["text"])

    @patch("website.views.send_inquiry_notification", return_value=True)
    def test_ajax_success_and_blog_source(self, notify):
        self.client.force_login(self.user)
        response = self._post(reverse("blog_detail", args=[self.post.slug]), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        inquiry = ContactInquiry.objects.get()
        self.assertEqual(inquiry.page_type, "Blog")
        self.assertEqual(inquiry.page_title, self.post.title)
        notify.assert_called_once_with(inquiry)

@override_settings(SECURE_SSL_REDIRECT=False)
class AuthenticationAndAdminAjaxTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="member", email="member@example.com", password="safe-test-password"
        )
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="safe-test-password"
        )

    def test_successful_login_uses_browser_session_and_updates_last_login(self):
        self.assertIsNone(self.user.last_login)
        response = self.client.post(reverse("login"), {"email": self.user.email, "password": "safe-test-password"})
        self.assertRedirects(response, reverse("home"))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertEqual(cookie["max-age"], "")
        self.assertEqual(cookie["expires"], "")
        self.assertTrue(self.client.session.get_expire_at_browser_close())
        self.assertFalse(settings.SESSION_SAVE_EVERY_REQUEST)

    def test_failed_login_does_not_update_last_login_and_logout_invalidates_session(self):
        self.client.post(reverse("login"), {"email": self.user.email, "password": "incorrect"})
        self.user.refresh_from_db()
        self.assertIsNone(self.user.last_login)
        self.client.post(reverse("login"), {"email": self.user.email, "password": "safe-test-password"})
        self.client.get(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.get(reverse("linkedin_connect"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_admin_ajax_users_filters_and_never_login_value(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:auth_user_ajax_users"), {"q": "member", "is_active": "1"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["users"]), 1)
        self.assertEqual(payload["users"][0]["last_login"], "Never")
        self.assertEqual(self.client.get(reverse("admin:auth_user_ajax_users"), {"is_active": "bad"}).status_code, 400)

    def test_admin_ajax_denies_normal_users_and_enforces_csrf_for_status_update(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("admin:auth_user_ajax_users")).status_code, 302)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        status_url = reverse("admin:auth_user_ajax_user_status", args=[self.user.pk])
        self.assertEqual(csrf_client.post(status_url, data='{"is_active": false}', content_type="application/json").status_code, 403)
        csrf_client.get(reverse("admin:auth_user_changelist"))
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(status_url, data='{"is_active": false}', content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_dashboard_statistics_endpoint_is_staff_only(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin_dashboard_stats"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_users"], 2)
@override_settings(SECURE_SSL_REDIRECT=False)
class ProtectedPageAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="protected-user", email="protected@example.com", password="safe-test-password")
        cls.category = ServiceCategory.objects.create(name="Protected advisory", slug="protected-advisory")
        cls.service = Service.objects.create(title="Protected service", slug="protected-service", category=cls.category, short_description="Guidance")
        cls.scheme = GovernmentScheme.objects.create(title="Protected scheme", slug="protected-scheme", short_description="Funding")
        cls.post = BlogPost.objects.create(title="Protected post", slug="protected-post", short_description="Guide", content="Content", author="FinGrow")

    def protected_urls(self):
        return [
            reverse("services"), reverse("service_category", args=[self.category.slug]), reverse("service_detail", args=[self.service.slug]),
            reverse("incubation_schemes"), reverse("incubation_scheme_detail", args=[self.scheme.slug]),
            reverse("blog"), reverse("blog_detail", args=[self.post.slug]),
        ]

    def test_home_and_contact_are_public(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("contact")).status_code, 200)

    def test_protected_content_redirects_anonymous_users_to_login(self):
        for url in self.protected_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_authenticated_browser_session_accesses_all_protected_content(self):
        self.client.post(reverse("login"), {"email": self.user.email, "password": "safe-test-password"})
        for url in self.protected_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_login_returns_to_the_original_protected_page(self):
        target = reverse("incubation_schemes")
        response = self.client.get(target)
        self.assertRedirects(response, f"{reverse('login')}?next={target}")
        response = self.client.post(f"{reverse('login')}?next={target}", {"email": self.user.email, "password": "safe-test-password"})
        self.assertRedirects(response, target)

    def test_logout_reprotects_content_but_not_public_pages(self):
        self.client.force_login(self.user)
        self.client.get(reverse("logout"))
        for url in self.protected_urls():
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("contact")).status_code, 200)