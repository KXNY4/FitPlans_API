import os

from .base import *  # noqa: F403, F405

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", os.getenv("DJANGO_ALLOWED_HOSTS", "")).split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost").split(",")

AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "True") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") == "True"
