# Security Report

## Fixed

- Removed the hard-coded secret fallback for production.
- Kept CSRF middleware and secure session/CSRF cookie defaults configurable by environment.
- Added clickjacking, MIME-sniffing, referrer, COOP/CORP, and proxy HTTPS protections.
- Added contact-form honeypot, validation, and per-IP throttling.
- Escaped sitemap XML output.

## Remaining risks

Use Redis-backed throttling in production, configure a restrictive CSP after inventorying required CDNs, set `DJANGO_ALLOWED_HOSTS` and trusted origins explicitly, and use HTTPS-only cookies/HSTS in the live environment. No password or token logging was found in the reviewed application code.
