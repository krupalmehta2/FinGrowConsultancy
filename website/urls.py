from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("process/", views.process, name="process"),
    path("services/", views.services, name="services"),
    path("services/category/<slug:slug>/", views.service_category, name="service_category"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("government-schemes/", views.government_schemes, name="government_schemes"),
    path("government-schemes/<slug:slug>/", views.government_scheme_detail, name="government_scheme_detail"),
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
