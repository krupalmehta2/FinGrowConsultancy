# Website Audit Report

## Executive summary

The Django site is structurally healthy and already includes CSRF protection, ORM queries, canonical/OG metadata, custom 404 handling, and dynamic `robots.txt`/`sitemap.xml`. The main production risks were a source-controlled fallback secret, weak contact-form abuse protection, and incomplete operational documentation.

## Fixes applied

- Made `DJANGO_SECRET_KEY` mandatory whenever `DEBUG=False` and removed the hard-coded production secret.
- Added `BigAutoField` as the project default to remove migration warnings for new models.
- Added a honeypot field and minimum-message validation to contact inquiries.
- Added a one-minute per-IP submission throttle using Django’s cache framework.
- Escaped sitemap XML locations before rendering.
- Added production-oriented security settings for content sniffing, browser XSS filtering, cross-origin resource policy, proxy HTTPS, and cookie flags.
- Added missing honeypot markup to contact forms on detail pages.

## Remaining recommendations

Set a production cache backend (Redis or Memcached), run `collectstatic`, serve media through a controlled storage layer, configure HTTPS/HSTS only after TLS is verified, and run Lighthouse against the deployed host. Analytics were intentionally not added.

## Severity

Critical: none found in the reviewed code. High: production secret fallback (fixed). Medium: form abuse controls and XML escaping (fixed). Low: external production performance and server configuration require deployment verification.
