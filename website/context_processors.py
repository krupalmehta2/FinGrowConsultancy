from .models import BlogPost, ContactInquiry, GovernmentScheme, Service, ServiceCategory, WebsiteSettings


def website_settings(request):
    return {
        "website_settings": WebsiteSettings.objects.first(),
        # Keep navigation driven by the active records in the admin.
        "nav_services": Service.objects.filter(active=True)[:5],
        "nav_categories": ServiceCategory.objects.filter(is_active=True),
        "footer_categories": ServiceCategory.objects.filter(is_active=True),
        "nav_schemes": GovernmentScheme.objects.filter(active=True)[:5],
        "footer_services": Service.objects.filter(active=True)[:6],
        "footer_schemes": GovernmentScheme.objects.filter(active=True)[:6],
    }


def admin_dashboard(request):
    """Small, admin-only dashboard context; never queried on public pages."""
    if not request.path.startswith("/admin") or not request.user.is_staff:
        return {}
    return {
        "admin_company": WebsiteSettings.objects.first(),
        "admin_counts": {
            "services": Service.objects.count(),
            "active_services": Service.objects.filter(active=True).count(),
            "schemes": GovernmentScheme.objects.count(),
            "active_schemes": GovernmentScheme.objects.filter(active=True).count(),
            "posts": BlogPost.objects.count(),
            "active_posts": BlogPost.objects.filter(active=True).count(),
            "inquiries": ContactInquiry.objects.count(),
            "new_inquiries": ContactInquiry.objects.filter(status=ContactInquiry.Status.NEW).count(),
        },
        "recent_inquiries": ContactInquiry.objects.order_by("-created_at")[:5],
    }
