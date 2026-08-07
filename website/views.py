from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.core.cache import cache
from django.utils.html import escape
from django.urls import reverse

from .forms import ContactInquiryForm
from .models import BlogPost, GovernmentScheme, Service


def save_inquiry(request):
    rate_key = f"contact-form:{request.META.get('REMOTE_ADDR', 'unknown')}"
    if cache.get(rate_key):
        messages.error(request, "Please wait a moment before sending another message.")
        return False
    form = ContactInquiryForm(request.POST)
    if form.is_valid():
        form.save()
        cache.set(rate_key, True, 60)
        messages.success(request, "Thank you. We will contact you shortly.")
        return True
    return False

def home(request):
    services = Service.objects.filter(active=True)[:3]
    posts = BlogPost.objects.filter(active=True, featured=True)[:3]
    return render(request, "home.html", {"services": services, "latest_posts": posts})

def about(request):
    return render(request, "about.html")

def process(request):
    return render(request, "process.html")

def services(request):
    services = Service.objects.filter(active=True)
    return render(request, "services.html", {"services": services})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, active=True)
    form = ContactInquiryForm()
    if request.method == "POST":
        if save_inquiry(request):
            return redirect("service_detail", slug=service.slug)
        form = ContactInquiryForm(request.POST)
    related_services = Service.objects.filter(active=True).exclude(pk=service.pk)[:3]
    latest_posts = BlogPost.objects.filter(active=True)[:4]
    return render(
        request,
        "service_detail.html",
        {
            "service": service,
            "form": form,
            "related_services": related_services,
            "latest_posts": latest_posts,
        },
    )

def government_schemes(request):
    schemes = GovernmentScheme.objects.filter(active=True)
    return render(request, "government_schemes.html", {"schemes": schemes})


def government_scheme_detail(request, slug):
    scheme = get_object_or_404(GovernmentScheme, slug=slug, active=True)
    form = ContactInquiryForm()
    if request.method == "POST":
        if save_inquiry(request):
            return redirect("government_scheme_detail", slug=scheme.slug)
        form = ContactInquiryForm(request.POST)
    related_schemes = GovernmentScheme.objects.filter(active=True).exclude(pk=scheme.pk)[:3]
    return render(
        request,
        "government_scheme_detail.html",
        {
            "scheme": scheme,
            "form": form,
            "related_schemes": related_schemes,
        },
    )

def blog(request):
    posts = BlogPost.objects.filter(active=True)
    return render(request, "blog.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, active=True)
    form = ContactInquiryForm()
    if request.method == "POST":
        if save_inquiry(request):
            return redirect("blog_detail", slug=post.slug)
        form = ContactInquiryForm(request.POST)
    related_posts = BlogPost.objects.filter(active=True).exclude(pk=post.pk)[:3]
    latest_posts = BlogPost.objects.filter(active=True).exclude(pk=post.pk)[:5]
    recent_services = Service.objects.filter(active=True)[:5]
    schemes = GovernmentScheme.objects.filter(active=True)[:5]
    return render(
        request,
        "blog_detail.html",
        {
            "post": post,
            "form": form,
            "related_posts": related_posts,
            "latest_posts": latest_posts,
            "recent_services": recent_services,
            "schemes": schemes,
        },
    )

def contact(request):
    if request.method == "POST":
        if save_inquiry(request):
            return redirect("contact")
        form = ContactInquiryForm(request.POST)
    else:
        form = ContactInquiryForm()
    return render(request, "contact.html", {"form": form})

def privacy_policy(request):
    return render(request, "privacy_policy.html")

def terms(request):
    return render(request, "terms.html")

def refund_policy(request):
    return render(request, "refund_policy.html")

def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap_xml"))
    return HttpResponse(
        "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /media/\n\nSitemap: " + sitemap_url + "\n",
        content_type="text/plain",
    )

def sitemap_xml(request):
    names = ["home", "about", "process", "services", "government_schemes", "blog", "contact", "privacy_policy", "terms", "refund_policy"]
    urls = [request.build_absolute_uri(reverse(name)) for name in names]
    urls += [request.build_absolute_uri(reverse("service_detail", kwargs={"slug": item.slug})) for item in Service.objects.filter(active=True)]
    urls += [request.build_absolute_uri(reverse("government_scheme_detail", kwargs={"slug": item.slug})) for item in GovernmentScheme.objects.filter(active=True)]
    urls += [request.build_absolute_uri(reverse("blog_detail", kwargs={"slug": item.slug})) for item in BlogPost.objects.filter(active=True)]
    items = "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls)
    return HttpResponse('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + items + "</urlset>", content_type="application/xml")

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_403(request, exception):
    return render(request, "403.html", status=403)

def custom_500(request):
    return render(request, "500.html", status=500)
