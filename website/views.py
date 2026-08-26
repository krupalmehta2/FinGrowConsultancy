from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ContactInquiryForm, LoginForm, RegistrationForm
from .models import BlogPost, CustomerProfile, GovernmentScheme, LinkedInConnection, LinkedInPost, NewsletterSubscriber, Service, ServiceCategory, SocialIdentity
from .linkedin import LinkedInError, authorization_url, connect
from . import social_auth
import secrets


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
    categories = ServiceCategory.objects.filter(is_active=True).order_by("display_order", "name")
    posts = BlogPost.objects.filter(active=True, featured=True)[:3]
    return render(request, "home.html", {"categories": categories, "latest_posts": posts})

def about(request):
    return render(request, "about.html")

def _safe_next(request):
    target = request.session.pop("linkedin_login_next", None) or request.GET.get("next")
    return target if target and url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()) else "home"


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Registration successful. You are now signed in.")
        return redirect(_safe_next(request))
    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(_safe_next(request))
    return render(request, "login.html", {"form": form})


def linkedin_login(request):
    if not social_auth.configured():
        messages.error(request, "LinkedIn sign-in is not configured yet.")
        return redirect("login")
    state = secrets.token_urlsafe(32)
    request.session["linkedin_login_state"] = state
    request.session["linkedin_login_next"] = request.GET.get("next", "")
    return redirect(social_auth.authorization_url(state))


def linkedin_callback(request):
    expected_state = request.session.pop("linkedin_login_state", None)
    if not expected_state or not secrets.compare_digest(request.GET.get("state", ""), expected_state):
        messages.error(request, "Your LinkedIn sign-in session expired. Please try again.")
        return redirect("login")
    if request.GET.get("error"):
        messages.error(request, "LinkedIn sign-in was cancelled or could not be completed.")
        return redirect("login")
    try:
        profile = social_auth.userinfo(social_auth.exchange_code(request.GET["code"]))
    except (KeyError, social_auth.LinkedInOIDCError):
        messages.error(request, "LinkedIn sign-in could not be completed. Please try again.")
        return redirect("login")
    identity = SocialIdentity.objects.select_related("user").filter(provider="linkedin", provider_user_id=profile["sub"]).first()
    email = (profile.get("email") or "").strip().lower() if profile.get("email_verified") is True else ""
    if identity:
        user = identity.user
    elif email:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create_user(username=email, email=email)
            user.set_unusable_password()
            user.first_name, user.last_name = profile.get("given_name", ""), profile.get("family_name", "")
            user.save()
            CustomerProfile.objects.create(user=user, full_name=profile.get("name") or " ".join(filter(None, (user.first_name, user.last_name))) or email)
        SocialIdentity.objects.create(provider="linkedin", provider_user_id=profile["sub"], user=user, email=email, name=profile.get("name", ""), first_name=profile.get("given_name", ""), last_name=profile.get("family_name", ""), profile_picture=profile.get("picture", ""))
    else:
        messages.error(request, "LinkedIn did not share an email address. Please register with email first, then try again.")
        return redirect("register")
    login(request, user)
    return redirect(_safe_next(request))

def user_logout(request):
    logout(request)
    return redirect("home")

def validate_registration_field(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "message": "Invalid request."}, status=405)
    field = request.POST.get("field", "")
    value = request.POST.get("value", "").strip()
    valid, message = True, ""
    if field == "email":
        from django.core.validators import validate_email
        try:
            validate_email(value)
            if User.objects.filter(email__iexact=value).exists():
                valid, message = False, "This email address is already registered."
        except ValidationError:
            valid, message = False, "Enter a valid email address."
    else:
        valid, message = False, "Unknown field."
    return JsonResponse({"valid": valid, "message": message})

@login_required
def process(request):
    return render(request, "process.html")

@login_required
def services(request):
    return render(request, "services.html", {"categories": ServiceCategory.objects.filter(is_active=True).order_by("display_order", "name")})

@login_required
def service_category(request, slug):
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    return render(request, "service_category.html", {"category": category, "services": category.services.filter(active=True).order_by("display_order", "title")})


@login_required
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

@login_required
def government_schemes(request):
    schemes = GovernmentScheme.objects.filter(active=True)
    return render(request, "government_schemes.html", {"schemes": schemes})


@login_required
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

@login_required
def blog(request):
    posts = BlogPost.objects.filter(active=True)
    return render(request, "blog.html", {"posts": posts, "linkedin_posts": LinkedInPost.objects.all()})

@user_passes_test(lambda user: user.is_staff)
def linkedin_connect(request):
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_ADMIN_REDIRECT_URI:
        messages.error(request, "Set LinkedIn credentials and redirect URI in the environment first.")
        return redirect("admin:index")
    state = secrets.token_urlsafe(32)
    request.session["linkedin_oauth_state"] = state
    return redirect(authorization_url(state))

@user_passes_test(lambda user: user.is_staff)
def linkedin_admin_callback(request):
    if request.GET.get("state") != request.session.pop("linkedin_oauth_state", None):
        messages.error(request, "LinkedIn OAuth state validation failed.")
        return redirect("admin:index")
    try:
        connect(request.GET["code"])
        messages.success(request, "LinkedIn connected successfully.")
    except (KeyError, LinkedInError) as error:
        messages.error(request, str(error))
    return redirect("admin:index")

@user_passes_test(lambda user: user.is_staff)
def linkedin_disconnect(request):
    if request.method == "POST":
        LinkedInConnection.objects.all().delete()
        messages.success(request, "LinkedIn disconnected.")
    return redirect("admin:index")


@login_required
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

def newsletter_subscribe(request):
    if request.method == "POST":
        email = request.POST.get("newsletter_email", "").strip().lower()
        if email:
            from django.core.validators import validate_email
            try:
                validate_email(email)
                NewsletterSubscriber.objects.get_or_create(email=email)
                messages.success(request, "Thanks for subscribing to FinGrow insights.")
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
        else:
            messages.error(request, "Please enter your email address.")
    return redirect(request.META.get("HTTP_REFERER", "/"))

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
