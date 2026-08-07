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
