from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/validate/", views.validate_registration_field, name="validate_registration_field"),
    path("process/", views.process, name="process"),
    path("services/", views.services, name="services"),
    path("services/category/<slug:slug>/", views.service_category, name="service_category"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("incubation-schemes/", views.incubation_schemes, name="incubation_schemes"),
    path("incubation-schemes/<slug:slug>/", views.incubation_scheme_detail, name="incubation_scheme_detail"),
    # Preserve bookmarked Government Scheme URLs while making Incubation Scheme canonical.
    path("government-schemes/", RedirectView.as_view(url="/incubation-schemes/", permanent=True), name="government_schemes"),
    path("government-schemes/<slug:slug>/", RedirectView.as_view(pattern_name="incubation_scheme_detail", permanent=True), name="government_scheme_detail"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms/", views.terms, name="terms"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
