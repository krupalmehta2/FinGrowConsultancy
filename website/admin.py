import csv
import json
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils.html import format_html
from django.utils import formats, timezone
from django.urls import path
from django.db.models import Q

from .models import BlogPost, ContactInquiry, GovernmentScheme, NewsletterSubscriber, Service, ServiceCategory, WebsiteSettings

admin.site.site_header = "FinGrow Administration"
admin.site.site_title = "FinGrow Admin"
admin.site.index_title = "Website Management"


class ImagePreviewMixin:
    readonly_fields = ("image_preview",)

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        image = getattr(obj, "icon", None) or getattr(obj, "featured_image", None) or getattr(obj, "image", None) or getattr(obj, "logo", None)
        if image:
            return format_html(
                '<img src="{}" style="max-width: 220px; max-height: 120px; border-radius: 8px;" />',
                image.url,
            )
        return "No image uploaded"


@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("logo", "favicon", "company_name", "image_preview")}),
        (
            "Contact",
            {
                "fields": (
                    "phone",
                    "alternate_phone",
                    "email",
                    "whatsapp",
                    "address",
                    "google_maps_embed",
                    "office_hours",
                )
            },
        ),
        ("Social Links", {"fields": ("facebook", "instagram", "linkedin", "youtube")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
        ("Footer", {"fields": ("copyright",)}),
    )
    readonly_fields = ("image_preview",)

    @admin.display(description="Logo Preview")
    def image_preview(self, obj):
        if obj and obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 220px; max-height: 120px; border-radius: 8px;" />',
                obj.logo.url,
            )
        return "No logo uploaded"

    def has_add_permission(self, request):
        if WebsiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Service)
class ServiceAdmin(ImagePreviewMixin, admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        return (("Content", {"fields": ("title", "slug", "category", "short_description", "description", "benefits", "process", "icon_class")}), ("Media", {"fields": ("icon", "featured_image", "image_preview")}), ("Publishing", {"fields": ("display_order", "active")}))

    list_display = ("title", "slug", "display_order", "active", "created_at", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("title", "short_description")
    ordering = ("display_order", "title")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "short_description", "description", "benefits", "process", "icon_class")}),
        ("Media", {"fields": ("icon", "featured_image", "image_preview")}),
        ("Publishing", {"fields": ("display_order", "active")}),
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")
    fieldsets = (("Content", {"fields": ("name", "slug", "description", "image", "image_preview")}), ("Publishing", {"fields": ("display_order", "is_active")}))


@admin.register(GovernmentScheme)
class GovernmentSchemeAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("title", "slug", "display_order", "active", "created_at", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("title", "short_description")
    ordering = ("display_order", "title")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "short_description", "description", "eligibility", "benefits", "required_documents")}),
        ("Media", {"fields": ("featured_image", "image_preview")}),
        ("Publishing", {"fields": ("display_order", "active")}),
    )


@admin.register(BlogPost)
class BlogPostAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("title", "slug", "author", "published_date", "featured", "active", "created_at")
    list_filter = ("active", "featured", "published_date", "created_at")
    search_fields = ("title", "short_description", "content", "author")
    ordering = ("-published_date", "-created_at")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "short_description", "content")}),
        ("Media", {"fields": ("featured_image", "image_preview")}),
        ("Publishing", {"fields": ("author", "published_date", "featured", "active")}),
    )


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "subject", "page_type", "status", "created_at")
    list_filter = ("status", "page_type", "created_at")
    search_fields = ("name", "phone", "email", "subject", "message", "page_title")
    ordering = ("-created_at",)
    readonly_fields = (
        "name",
        "phone",
        "email",
        "subject",
        "message",
        "page_type",
        "page_title",
        "current_url",
        "created_at",
    )

    def has_add_permission(self, request):
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    actions = ("export_csv",)

    @admin.action(description="Download selected subscribers as CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="fingrow-newsletter-subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(["Email", "Subscribed at", "Active"])
        for subscriber in queryset.order_by("email"):
            writer.writerow([subscriber.email, subscriber.subscribed_at.isoformat(), "Yes" if subscriber.is_active else "No"])
        return response

# Re-register Django's built-in User admin.  The normal UserAdmin screens,
# permissions, actions and edit behavior remain intact; only the changelist
# gains small staff-only JSON helpers for its AJAX controls.
admin.site.unregister(User)


@admin.register(User)
class FinGrowUserAdmin(UserAdmin):
    list_display = (
        "username", "email", "first_name", "last_name", "is_active",
        "is_staff", "is_superuser", "date_joined", "last_login_display",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "last_login", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    change_list_template = "admin/auth/user/change_list.html"

    class Media:
        js = ("admin/js/fingrow-users.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("ajax/users/", self.admin_site.admin_view(self.ajax_users), name="auth_user_ajax_users"),
            path("ajax/users/<int:user_id>/status/", self.admin_site.admin_view(self.ajax_user_status), name="auth_user_ajax_user_status"),
        ]
        return custom_urls + urls

    def _ajax_permission_denied(self, request):
        return JsonResponse({"detail": "You do not have permission to view users."}, status=403)

    def _filtered_users(self, request):
        params = request.GET
        queryset = self.get_queryset(request)
        query = params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
                | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        for field in ("is_active", "is_staff", "is_superuser"):
            value = params.get(field)
            if value in {"0", "1"}:
                queryset = queryset.filter(**{field: value == "1"})
            elif value not in {None, ""}:
                raise ValueError(f"Invalid {field} filter.")
        last_login = params.get("last_login")
        if last_login == "never":
            queryset = queryset.filter(last_login__isnull=True)
        elif last_login == "today":
            queryset = queryset.filter(last_login__date=timezone.localdate())
        elif last_login not in {None, ""}:
            raise ValueError("Invalid last_login filter.")
        date_joined = params.get("date_joined")
        if date_joined == "today":
            queryset = queryset.filter(date_joined__date=timezone.localdate())
        elif date_joined not in {None, ""}:
            raise ValueError("Invalid date_joined filter.")
        return queryset.order_by(*self.get_ordering(request))

    @admin.display(description="Last login", ordering="last_login")
    def last_login_display(self, obj):
        return formats.date_format(timezone.localtime(obj.last_login), "DATETIME_FORMAT") if obj.last_login else "Never"

    def ajax_users(self, request):
        if request.method != "GET":
            return JsonResponse({"detail": "Method not allowed."}, status=405)
        if not self.has_view_permission(request):
            return self._ajax_permission_denied(request)
        try:
            users = self._filtered_users(request)[:100]
        except ValueError as exc:
            return JsonResponse({"detail": str(exc)}, status=400)
        return JsonResponse({"users": [
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_joined": formats.date_format(timezone.localtime(user.date_joined), "DATETIME_FORMAT"),
                "last_login": self.last_login_display(user),
                "change_url": f"../{user.pk}/change/",
            }
            for user in users
        ], "truncated": users.count() == 100})

    def ajax_user_status(self, request, user_id):
        if request.method != "POST":
            return JsonResponse({"detail": "Method not allowed."}, status=405)
        try:
            payload = json.loads(request.body or "{}")
        except (TypeError, json.JSONDecodeError):
            return JsonResponse({"detail": "Invalid JSON payload."}, status=400)
        is_active = payload.get("is_active")
        if type(is_active) is not bool:
            return JsonResponse({"detail": "is_active must be a boolean."}, status=400)
        try:
            user = self.get_queryset(request).get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({"detail": "User not found."}, status=404)
        if user.pk == request.user.pk or not self.has_change_permission(request, user):
            return JsonResponse({"detail": "You do not have permission to update this user."}, status=403)
        user.is_active = is_active
        user.save(update_fields=("is_active",))
        return JsonResponse({"id": user.pk, "is_active": user.is_active})