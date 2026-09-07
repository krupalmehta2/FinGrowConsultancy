# Hostinger Ubuntu deployment

## Prepare the server

Install Ubuntu packages: `python3`, `python3-venv`, `python3-pip`, `nginx`, `git`, and `certbot` with the Nginx plugin. Clone the repository into `/var/www/fingrow`, create a virtual environment, and install `requirements.txt`.

## Configure and migrate

Copy `.env.example` to `.env` (or export the same variables through systemd), set a long random `DJANGO_SECRET_KEY`, production hosts and HTTPS origins, then run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

## Gunicorn

Run from the project directory: `gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60`. Use a systemd service for restart-on-failure and an Nginx reverse proxy for `/`, `/static/`, and `/media/`.

## SSL and operations

Point DNS to the VPS, issue the certificate with Certbot, verify HTTP-to-HTTPS redirects, then enable HSTS. Back up `db.sqlite3` and `media/` regularly. Never commit `.env`, the database, virtual environments, or runtime static output.

## Render demo deployment

Create a Render Blueprint from `render.yaml`, or connect the `main` branch as a Python Web Service. The included SQLite database and local media are suitable for a temporary demo only; use PostgreSQL and durable/object storage before a client production launch.

For this temporary demo, the existing `db.sqlite3` is deployed with the repository. Do not run seed or reset commands. Render Free uses ephemeral storage, so database changes can disappear after a rebuild or restart; use a persistent disk if this demo must retain changes.

## Resend inquiry notifications

This site sends saved customer inquiries through the Resend transactional email API; it does not require the visitor to have an email application or account. Verify a sending domain/address in Resend first, then place the following in a root-owned systemd environment file such as `/etc/fingrow/fingrow.env` (do not add it to Git):

```ini
RESEND_API_KEY=your-resend-api-key
INQUIRY_NOTIFICATION_FROM=FinGrow Consultancy Services <notifications@your-verified-domain.example>
INQUIRY_NOTIFICATION_TO=fingrowconsultancyservices@gmail.com
```

Restrict the file with `sudo chown root:root /etc/fingrow/fingrow.env` and `sudo chmod 600 /etc/fingrow/fingrow.env`. In the Gunicorn service unit, add `EnvironmentFile=/etc/fingrow/fingrow.env` under `[Service]`, then run `sudo systemctl daemon-reload` and `sudo systemctl restart fingrow`. Confirm the address/domain is verified by Resend before testing.

To test production, submit each inquiry form once with a real address, confirm the success message and the new Contact Inquiry record in Django admin, then confirm the notification arrives at `fingrowconsultancyservices@gmail.com` with the visitor as Reply-To. If Resend is unavailable, the inquiry remains stored and the server logs the delivery failure without exposing configuration to the visitor.
