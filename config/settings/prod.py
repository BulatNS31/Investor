import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import SECRET_KEY, env_list  # noqa: F401

DEBUG = False


if not SECRET_KEY or len(SECRET_KEY) < 50 or SECRET_KEY.startswith("django-insecure-"):
	raise ImproperlyConfigured(
		"SECRET_KEY должен быть длинным (50+ символов) случайным значением из окружения."
	)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
	raise ImproperlyConfigured("Задайте ALLOWED_HOSTS в окружении (например, example.com).")

if not os.getenv("DB_PASSWORD"):
	raise ImproperlyConfigured("Задайте DB_PASSWORD в окружении.")

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")


SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
JWT_AUTH_COOKIE_SECURE = True


SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
