import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import BlogPost, LinkedInConnection, LinkedInPost

logger = logging.getLogger(__name__)


class LinkedInError(Exception):
    pass


def _request(url, method="GET", data=None, headers=None):
    request = urllib.request.Request(url, method=method, data=json.dumps(data).encode() if data is not None else None, headers={"Accept": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, dict(response.headers), json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        body = error.read().decode(errors="replace")[:1000]
        raise LinkedInError(f"LinkedIn API returned HTTP {error.code}: {body}") from error
    except (urllib.error.URLError, json.JSONDecodeError) as error:
        raise LinkedInError("LinkedIn is temporarily unavailable.") from error


def authorization_url(state):
    query = urllib.parse.urlencode({"response_type": "code", "client_id": settings.LINKEDIN_CLIENT_ID, "redirect_uri": settings.LINKEDIN_ADMIN_REDIRECT_URI, "state": state, "scope": settings.LINKEDIN_ADMIN_SCOPES})
    return f"https://www.linkedin.com/oauth/v2/authorization?{query}"


def connect(code):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    body = urllib.parse.urlencode({"grant_type": "authorization_code", "code": code, "redirect_uri": settings.LINKEDIN_ADMIN_REDIRECT_URI, "client_id": settings.LINKEDIN_CLIENT_ID, "client_secret": settings.LINKEDIN_CLIENT_SECRET}).encode()
    request = urllib.request.Request(token_url, method="POST", data=body, headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            token = json.loads(response.read().decode())
    except Exception as error:
        raise LinkedInError("LinkedIn authorization failed.") from error
    access_token = token.get("access_token")
    if not access_token:
        raise LinkedInError("LinkedIn did not return an access token.")
    profile = _api("/v2/userinfo", access_token)[2]
    connection, _ = LinkedInConnection.objects.update_or_create(defaults={"access_token": access_token, "expires_at": timezone.now() + timedelta(seconds=int(token.get("expires_in", 5184000))), "member_id": profile.get("sub", ""), "member_name": profile.get("name", ""), "member_picture": profile.get("picture", ""), "last_error": ""})
    return connection


def _api(path, token, data=None, method="GET"):
    return _request("https://api.linkedin.com" + path, method, data, {"Authorization": f"Bearer {token}", "Linkedin-Version": settings.LINKEDIN_API_VERSION, "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"})


def publish_blog(blog, request):
    connection = LinkedInConnection.current()
    if not connection:
        return False
    if blog.linkedin_post_id:
        return True
    blog.linkedin_publish_attempts += 1
    try:
        if connection.expires_at <= timezone.now():
            raise LinkedInError("LinkedIn access token has expired. Reconnect from Admin.")
        url = request.build_absolute_uri(reverse("blog_detail", kwargs={"slug": blog.slug}))
        text = f"{blog.title}\n\n{blog.short_description}\n\nRead the complete article:\n{url}\n\n#FinGrow #BusinessGrowth #Entrepreneurship"
        payload = {"author": f"urn:li:person:{connection.member_id}", "commentary": {"text": text}, "visibility": "PUBLIC", "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []}, "lifecycleState": "PUBLISHED", "content": {"article": {"source": url, "title": blog.title, "description": blog.short_description}}}
        status, headers, _ = _api("/rest/posts", connection.access_token, payload, "POST")
        post_id = headers.get("x-restli-id") or headers.get("X-RestLi-Id")
        if status not in (200, 201) or not post_id:
            raise LinkedInError("LinkedIn did not return a post ID.")
        blog.linkedin_published = True
        blog.linkedin_post_id = post_id
        blog.linkedin_post_url = f"https://www.linkedin.com/feed/update/{urllib.parse.quote(post_id, safe=':/')}"
        blog.linkedin_published_at = timezone.now()
        blog.linkedin_last_error = ""
        blog.save(update_fields=["linkedin_published", "linkedin_post_id", "linkedin_post_url", "linkedin_published_at", "linkedin_last_error", "linkedin_publish_attempts"])
        return True
    except LinkedInError as error:
        logger.warning("LinkedIn publication failed for blog %s: %s", blog.pk, error)
        blog.linkedin_last_error = str(error)
        blog.save(update_fields=["linkedin_last_error", "linkedin_publish_attempts"])
        return False
