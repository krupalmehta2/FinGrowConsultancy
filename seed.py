import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from website.models import Service

services = [
    {
        "title": "Business Incorporation",
        "slug": "business-incorporation",
        "short_description": "Private Limited, LLP, OPC and Partnership firm registration.",
        "display_order": 1,
    },
    {
        "title": "Startup India & DPIIT Recognition",
        "slug": "startup-india-dpiit-recognition",
        "short_description": "End-to-end Startup India and DPIIT registration support.",
        "display_order": 2,
    },
    {
        "title": "MSME / Udyam Registration",
        "slug": "msme-udyam-registration",
        "short_description": "MSME registration and government benefits assistance.",
        "display_order": 3,
    },
    {
        "title": "Government Funding Assistance",
        "slug": "government-funding-assistance",
        "short_description": "Support for grants, subsidies and government funding.",
        "display_order": 4,
    },
    {
        "title": "Government Scheme Consultancy",
        "slug": "government-scheme-consultancy",
        "short_description": "Expert guidance for central and state government schemes.",
        "display_order": 5,
    },
    {
        "title": "Business Registration & Licensing",
        "slug": "business-registration-licensing",
        "short_description": "Complete registration and licensing solutions.",
        "display_order": 6,
    },
    {
        "title": "GST Registration & Compliance",
        "slug": "gst-registration-compliance",
        "short_description": "GST registration, filing and compliance support.",
        "display_order": 7,
    },
    {
        "title": "IEC Registration",
        "slug": "iec-registration",
        "short_description": "Import Export Code registration services.",
        "display_order": 8,
    },
    {
        "title": "Trademark Registration",
        "slug": "trademark-registration",
        "short_description": "Trademark filing and intellectual property protection.",
        "display_order": 9,
    },
    {
        "title": "ISO Certification",
        "slug": "iso-certification",
        "short_description": "Consultancy for ISO certification and compliance.",
        "display_order": 10,
    },
    {
        "title": "FSSAI Registration",
        "slug": "fssai-registration",
        "short_description": "Food license registration and consultancy.",
        "display_order": 11,
    },
    {
        "title": "Compliance & Tax Advisory",
        "slug": "compliance-tax-advisory",
        "short_description": "Business compliance and taxation advisory.",
        "display_order": 12,
    },
    {
        "title": "Business Growth Consulting",
        "slug": "business-growth-consulting",
        "short_description": "Strategic business planning and growth advisory.",
        "display_order": 13,
    },
    {
        "title": "Funding & Loan Assistance",
        "slug": "funding-loan-assistance",
        "short_description": "Business loan and financial assistance consulting.",
        "display_order": 14,
    },
    {
        "title": "Working Capital Support",
        "slug": "working-capital-support",
        "short_description": "Working capital planning and funding guidance.",
        "display_order": 15,
    },
    {
        "title": "Subsidy & Incentive Consultancy",
        "slug": "subsidy-incentive-consultancy",
        "short_description": "Identify and apply for government subsidies.",
        "display_order": 16,
    },
    {
        "title": "Business Expansion Advisory",
        "slug": "business-expansion-advisory",
        "short_description": "Expansion strategy for growing businesses.",
        "display_order": 17,
    },
    {
        "title": "Technology Upgradation Support",
        "slug": "technology-upgradation-support",
        "short_description": "Support for technology modernization schemes.",
        "display_order": 18,
    },
    {
        "title": "Export Promotion Assistance",
        "slug": "export-promotion-assistance",
        "short_description": "Guidance for export incentives and international business.",
        "display_order": 19,
    },
    {
        "title": "Financial Planning & Advisory",
        "slug": "financial-planning-advisory",
        "short_description": "Financial planning and business advisory services.",
        "display_order": 20,
    },
    {
        "title": "SME IPO Advisory",
        "slug": "sme-ipo-advisory",
        "short_description": "Complete consultancy for SME IPO listing.",
        "display_order": 21,
    },
    {
        "title": "Main Board IPO Advisory",
        "slug": "main-board-ipo-advisory",
        "short_description": "End-to-end IPO advisory and listing support.",
        "display_order": 22,
    },
    {
        "title": "Merchant Banker Coordination",
        "slug": "merchant-banker-coordination",
        "short_description": "Coordination with merchant bankers and intermediaries.",
        "display_order": 23,
    },
    {
        "title": "Investor Readiness Consulting",
        "slug": "investor-readiness-consulting",
        "short_description": "Business preparation for investors and fundraising.",
        "display_order": 24,
    },
    {
        "title": "Business Consultancy Services",
        "slug": "business-consultancy-services",
        "short_description": "Comprehensive consultancy for startups, MSMEs and enterprises.",
        "display_order": 25,
    },
]

created = 0
updated = 0

for service in services:
    obj, is_created = Service.objects.update_or_create(
        slug=service["slug"],
        defaults=service,
    )

    if is_created:
        created += 1
        print(f"Created: {obj.title}")
    else:
        updated += 1
        print(f"Updated: {obj.title}")

print("\n" + "=" * 50)
print(f"Total Services : {len(services)}")
print(f"Created        : {created}")
print(f"Updated        : {updated}")
print("=" * 50)
print("Seeding completed successfully!")
