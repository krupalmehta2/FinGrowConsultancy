from django.contrib import admin
from django.utils.html import format_html

from .models import BlogPost, ContactInquiry, GovernmentScheme, Service, WebsiteSettings

admin.site.site_header = "FinGrow Administration"
admin.site.site_title = "FinGrow Admin"
admin.site.index_title = "Website Management"


class ImagePreviewMixin:
    readonly_fields = ("image_preview",)

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        image = getattr(obj, "featured_image", None) or getattr(obj, "logo", None)
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
    list_display = ("title", "slug", "display_order", "active", "created_at", "updated_at")
    list_filter = ("active", "created_at", "updated_at")
    search_fields = ("title", "short_description")
    ordering = ("display_order", "title")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "short_description", "description", "benefits", "process", "icon_class")}),
        ("Media", {"fields": ("featured_image", "image_preview")}),
        ("Publishing", {"fields": ("display_order", "active")}),
    )


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
