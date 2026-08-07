# Production Deployment Audit

## Score: 86/100 before hosting

The application is Django/Gunicorn compatible and suitable for GitHub deployment. VPS readiness depends on the server service, Nginx, DNS, SSL, and backups being configured.

## Fixes applied

- Added environment-variable template for secrets, hosts, CSRF origins, cookies, email, cache, and HSTS.
- Added production logging, configurable email, cache readiness, and Permissions Policy configuration.
- Confirmed `DEFAULT_AUTO_FIELD`, static/media paths, secure proxy handling, cookie security, CSRF, clickjacking, MIME sniffing, and referrer policy.
- Added deployment runbook and retained dynamic robots/sitemap routes.
- Confirmed `.gitignore` excludes `.env`, SQLite database, virtual environments, pycache, logs, and `staticfiles`.

## Manual steps remaining

Configure the VPS systemd service, Nginx site, DNS, Certbot certificate, SMTP credentials, production cache backend, file permissions, and automated backups. Run Lighthouse against the live domain. HSTS must only be enabled after HTTPS is verified.

## Checklists

- Django: `migrate`, `collectstatic`, `check --deploy`.
- Security: random secret, `DEBUG=0`, exact hosts/origins, HTTPS, secure cookies, HSTS after verification.
- Nginx: proxy Gunicorn, serve static/media, compression, TLS, security headers.
- SEO: verify titles, canonicals, robots, sitemap, structured data, and live absolute URLs.
- GitHub: inspect `git status`, confirm no `.env`, `db.sqlite3`, backups, or secrets are staged.
- Operations: monitoring, rotation, database/media backups, and restore testing.

## Verdict

Ready for GitHub and Gunicorn. Ready for VPS, Nginx, SSL, and production after the documented manual hosting configuration is completed.
