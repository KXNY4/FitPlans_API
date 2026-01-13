from django.conf import settings

# This file helps AI tools to understand how to fix tests by providing a reusable way to set auth cookies.
# It is not used by the app itself, but can be imported in tests.


def auth_headers(tokens):
    """
    Deprecated: Use set_auth_cookies instead.
    """
    return {"Authorization": f"Bearer {tokens['access']}"}


def set_auth_cookies(client, tokens):
    """
    Sets authentication cookies for the TestClient.
    """
    client.cookies[settings.AUTH_COOKIE] = tokens["access"]
    client.cookies[settings.AUTH_COOKIE_REFRESH] = tokens["refresh"]
