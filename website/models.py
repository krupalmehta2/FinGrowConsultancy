from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class WebsiteSettings(models.Model):
    logo = models.ImageField(upload_to="settings/", blank=True, null=True)
    favicon = models.ImageField(upload_to="settings/", blank=True, null=True)
    company_name = models.CharField(max_length=150, default="FinGrow Consultancy Services")
    phone = models.CharField(max_length=30, blank=True)
    alternate_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    google_maps_embed = models.TextField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    office_hours = models.CharField(max_length=150, blank=True)
    copyright = models.CharField(max_length=255, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)

    class Meta:
        verbose_name = "Website Settings"
        verbose_name_plural = "Website Settings"

    def clean(self):
        if not self.pk and WebsiteSettings.objects.exists():
            raise ValidationError("Only one Website Settings record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


class Service(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.TextField()
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    process = models.TextField(blank=True)
    icon_class = models.CharField(max_length=100, blank=True)
    featured_image = models.ImageField(upload_to="services/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("service_detail", kwargs={"slug": self.slug})


class GovernmentScheme(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.TextField()
    description = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    required_documents = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to="government-schemes/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = "Government Scheme"
        verbose_name_plural = "Government Schemes"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("government_scheme_detail", kwargs={"slug": self.slug})


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    short_description = models.TextField()
    content = models.TextField()
    author = models.CharField(max_length=100)
    published_date = models.DateTimeField(default=timezone.now)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-published_date", "-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})


class ContactInquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    page_type = models.CharField(max_length=30, blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    current_url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} - {self.subject}"
