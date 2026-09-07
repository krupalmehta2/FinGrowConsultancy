"""Centralized transactional email notifications for saved customer inquiries."""
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


def send_inquiry_notification(inquiry):
    """Send one Resend notification after an inquiry has been stored safely."""
    api_key = settings.RESEND_API_KEY
    sender = settings.INQUIRY_NOTIFICATION_FROM
    recipient = settings.INQUIRY_NOTIFICATION_TO
    if not all((api_key, sender, recipient)):
        logger.warning("Inquiry %s saved, but transactional email is not configured.", inquiry.pk)
        return False

    inquiry_type = inquiry.page_type or "General"
    subject = f"NEW LEAD - {inquiry_type.upper()} INQUIRY"
    lines = [
        subject, "",
        f"Name: {inquiry.name}", f"Phone: {inquiry.phone}", f"Email: {inquiry.email}",
        f"Subject: {inquiry.subject}", f"Message: {inquiry.message or '-'}",
        f"Page Type: {inquiry.page_type or '-'}", f"Page Title: {inquiry.page_title or '-'}",
        f"Current URL: {inquiry.current_url or '-'}", f"Submitted At: {inquiry.created_at.isoformat()}",
    ]
    payload = json.dumps({
        "from": sender,
        "to": [recipient],
        "reply_to": inquiry.email,
        "subject": subject,
        "text": "\n".join(lines),
    }).encode("utf-8")
    request = Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"fingrow-inquiry-{inquiry.pk}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if 200 <= status < 300:
                return True
            logger.error("Inquiry %s notification returned HTTP %s.", inquiry.pk, status)
    except (HTTPError, URLError, TimeoutError, OSError):
        logger.exception("Inquiry %s notification failed after being saved.", inquiry.pk)
    return False