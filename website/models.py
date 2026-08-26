from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class WebsiteSettings(models.Model):
    logo = models.ImageField(upload_to="settings/", blank=True, null=True)
    hero_image = models.ImageField(upload_to="settings/", blank=True, null=True)
    about_hero_image = models.ImageField(upload_to="settings/", blank=True, null=True)
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


class ServiceCategory(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="service-categories/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Use 1 for the first category, 2 for the second, 3 for the third, and so on. Lower numbers appear first.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("service_category", kwargs={"slug": self.slug})


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    full_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.full_name


class SocialIdentity(models.Model):
    """A stable external provider identity linked to a local customer account."""
    provider = models.CharField(max_length=40)
    provider_user_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_identities")
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("provider", "provider_user_id"), name="unique_social_provider_identity")]

    def __str__(self):
        return f"{self.provider}: {self.provider_user_id}"

class Service(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.TextField()
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    process = models.TextField(blank=True)
    icon_class = models.CharField(max_length=100, blank=True)
    icon = models.ImageField(upload_to="services/icons/", blank=True, null=True, help_text="Optional custom icon. This is shown before the automatic icon.")
    featured_image = models.ImageField(upload_to="services/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="services")
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

    @property
    def fallback_icon_class(self):
        """Return a relevant icon when an editor has not specified one."""
        service_type = " ".join(filter(None, (self.title, self.short_description, self.category.name if self.category else ""))).lower()
        icon_map = (
            (("web development", "website", "web design", "software", "app development"), "fa-solid fa-laptop-code"),
            (("seo", "search engine", "digital marketing", "marketing"), "fa-solid fa-chart-line"),
            (("photography", "photographer", "photo shoot", "photoshoot"), "fa-solid fa-camera"),
            (("video", "editing", "film", "reel"), "fa-solid fa-video"),
            (("business growth", "growth", "business strategy", "analytics", "consulting"), "fa-solid fa-arrow-trend-up"),
        )
        for keywords, icon_class in icon_map:
            if any(keyword in service_type for keyword in keywords):
                return icon_class
        return "fa-solid fa-briefcase"

    @property
    def effective_icon_class(self):
        return self.icon_class or self.fallback_icon_class


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
    linkedin_published = models.BooleanField(default=False, editable=False)
    linkedin_post_id = models.CharField(max_length=255, blank=True, editable=False)
    linkedin_post_url = models.URLField(blank=True, editable=False)
    linkedin_published_at = models.DateTimeField(blank=True, null=True, editable=False)
    linkedin_last_error = models.TextField(blank=True, editable=False)
    linkedin_publish_attempts = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ["-published_date", "-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})


class LinkedInConnection(models.Model):
    access_token = models.TextField()
    expires_at = models.DateTimeField()
    member_id = models.CharField(max_length=255)
    member_name = models.CharField(max_length=255, blank=True)
    member_picture = models.URLField(blank=True)
    connected_at = models.DateTimeField(default=timezone.now, editable=False)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)

    class Meta:
        verbose_name = "LinkedIn Connection"
        verbose_name_plural = "LinkedIn Connection"

    def __str__(self):
        return f"LinkedIn: {self.member_name or self.member_id}"

    @classmethod
    def current(cls):
        return cls.objects.first()


class LinkedInPost(models.Model):
    linkedin_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    published_at = models.DateTimeField()
    linkedin_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    author_name = models.CharField(max_length=255, blank=True)
    author_picture = models.URLField(blank=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.linkedin_id


class ContactInquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField(blank=True)
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


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return self.email
