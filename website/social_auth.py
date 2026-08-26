import json
import urllib.parse
import urllib.request
import urllib.error

import jwt
from jwt import PyJWKClient
from django.conf import settings


class LinkedInOIDCError(Exception):
    pass


AUTHORIZATION_ENDPOINT = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_ENDPOINT = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_ENDPOINT = "https://api.linkedin.com/v2/userinfo"
JWKS_ENDPOINT = "https://www.linkedin.com/oauth/openid/jwks"
ISSUER = "https://www.linkedin.com"


def configured():
    return bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET and settings.LINKEDIN_REDIRECT_URI)


def authorization_url(state):
    query = urllib.parse.urlencode({
        "response_type": "code", "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI, "state": state,
        "scope": "openid profile email",
    })
    return f"{AUTHORIZATION_ENDPOINT}?{query}"


def _json_request(request):
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        raise LinkedInOIDCError("LinkedIn is temporarily unavailable. Please try again.") from exc


def exchange_code(code):
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }).encode()
    token = _json_request(urllib.request.Request(TOKEN_ENDPOINT, payload, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}))
    if not token.get("access_token") or not token.get("id_token"):
        raise LinkedInOIDCError("LinkedIn did not return a valid sign-in response.")
    try:
        signing_key = PyJWKClient(JWKS_ENDPOINT).get_signing_key_from_jwt(token["id_token"])
        jwt.decode(token["id_token"], signing_key.key, algorithms=["RS256"], audience=settings.LINKEDIN_CLIENT_ID, issuer=ISSUER)
    except (jwt.PyJWTError, jwt.PyJWKClientError) as exc:
        raise LinkedInOIDCError("LinkedIn sign-in could not be verified.") from exc
    return token["access_token"]


def userinfo(access_token):
    profile = _json_request(urllib.request.Request(USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}))
    if not profile.get("sub"):
        raise LinkedInOIDCError("LinkedIn did not return a valid account identifier.")
    return profile