from django.db import migrations


def create_categories_and_assign_services(apps, schema_editor):
    ServiceCategory = apps.get_model("website", "ServiceCategory")
    Service = apps.get_model("website", "Service")
    categories = {
        "startup-solutions": ("Startup Solutions", "End-to-end support for startups, funding opportunities and early-stage growth."),
        "business-registration": ("Business Registration", "Support for the right legal, statutory and registration structure."),
        "certification-services": ("Certification Services", "Guidance for certifications, licences and compliance requirements."),
        "government-funding": ("Government Funding", "Assistance identifying suitable grants, subsidies and financial support opportunities."),
        "business-growth-solutions": ("Business Growth Solutions", "Practical support for expansion, planning, working capital and business improvement."),
        "ipo-sme-ipo-advisory": ("IPO & SME IPO Advisory", "Advisory support for IPO readiness, financial structuring and investor preparation."),
    }
    created = {}
    old = ServiceCategory.objects.filter(slug="incubation-funding").first()
    for slug, (name, description) in categories.items():
        if slug == "government-funding" and old:
            continue
        category, _ = ServiceCategory.objects.update_or_create(slug=slug, defaults={"name": name, "description": description, "is_active": True})
        created[slug] = category
    if old:
        old.name = "Government Funding"
        old.slug = "government-funding"
        old.description = categories["government-funding"][1]
        old.save(update_fields=["name", "slug", "description"])
        created["government-funding"] = old
    for service in Service.objects.filter(category__isnull=True):
        title = service.title.lower()
        if any(word in title for word in ["startup", "dpiit", "investor"]):
            key = "startup-solutions"
        elif any(word in title for word in ["registration", "incorporation", "msme", "gst", "iec"]):
            key = "business-registration"
        elif any(word in title for word in ["iso", "fssai", "trademark", "certification"]):
            key = "certification-services"
        elif any(word in title for word in ["funding", "loan", "subsidy", "incentive", "scheme"]):
            key = "government-funding"
        elif "ipo" in title or "merchant banker" in title:
            key = "ipo-sme-ipo-advisory"
        else:
            key = "business-growth-solutions"
        service.category = created[key]
        service.save(update_fields=["category"])


class Migration(migrations.Migration):
    dependencies = [("website", "0004_newslettersubscriber")]
    operations = [migrations.RunPython(create_categories_and_assign_services, migrations.RunPython.noop)]
