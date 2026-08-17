from __future__ import annotations

from os import environ
from pathlib import Path
from shutil import which


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_ROOT = Path(__file__).resolve().parents[2]
DEBUG = environ.get("FLYWHEEL_DEBUG", "1") == "1"
SECRET_KEY = environ.get("FLYWHEEL_SECRET_KEY", "unsafe-local-development-key")
if not DEBUG and SECRET_KEY == "unsafe-local-development-key":
    raise RuntimeError("FLYWHEEL_SECRET_KEY is required when DEBUG is disabled")

ALLOWED_HOSTS = [host for host in environ.get("FLYWHEEL_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if host]
ROOT_URLCONF = "product.config.urls"
WSGI_APPLICATION = "product.config.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "product.campaign",
    "product.review",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [PRODUCT_ROOT / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": environ.get("FLYWHEEL_DB_NAME", "flywheel_dev"),
    "USER": environ.get("FLYWHEEL_DB_USER", ""),
    "PASSWORD": environ.get("FLYWHEEL_DB_PASSWORD", ""),
    "HOST": environ.get("FLYWHEEL_DB_HOST", ""),
    "PORT": environ.get("FLYWHEEL_DB_PORT", ""),
    "CONN_MAX_AGE": 0,
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "campaigns"
LOGOUT_REDIRECT_URL = "login"
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CAMPAIGN_ROOT = Path(
    environ.get("FLYWHEEL_CAMPAIGN_ROOT", PROTOTYPE_ROOT / "var" / "campaigns")
)
CAMPAIGN_ARTIFACT_MAX_BYTES = int(environ.get("FLYWHEEL_CAMPAIGN_ARTIFACT_MAX_BYTES", str(5 * 1024 * 1024)))
CAMPAIGN_JOB_MAX_SOURCES = int(
    environ.get("FLYWHEEL_CAMPAIGN_JOB_MAX_SOURCES", "12")
)
CAMPAIGN_JOB_MAX_INPUT_BYTES = int(
    environ.get("FLYWHEEL_CAMPAIGN_JOB_MAX_INPUT_BYTES", str(20 * 1024 * 1024))
)
NTM_BINARY = Path(environ.get("FLYWHEEL_NTM_BINARY", "/usr/local/bin/ntm"))
NTM_CONTROL_TIMEOUT_SECONDS = int(environ.get("FLYWHEEL_NTM_CONTROL_TIMEOUT_SECONDS", "90"))
CAMPAIGN_CODEX_MODEL = environ.get("FLYWHEEL_CAMPAIGN_CODEX_MODEL", "gpt-5.6-sol")
CAMPAIGN_CODEX_BINARY = environ.get(
    "FLYWHEEL_CAMPAIGN_CODEX_BINARY", which("codex") or ""
)
CAMPAIGN_CODEX_SKILL_ROOT = Path(
    environ.get("FLYWHEEL_CAMPAIGN_CODEX_SKILL_ROOT", Path.home() / ".codex" / "skills")
)
LANGFUSE_TARGET_BASE_URL = environ.get("FLYWHEEL_LANGFUSE_TARGET_BASE_URL", "")
LANGFUSE_TARGET_PROJECT_ID = environ.get(
    "FLYWHEEL_LANGFUSE_TARGET_PROJECT_ID", ""
)
LANGFUSE_READBACK_PAGE_LIMIT = int(
    environ.get("FLYWHEEL_LANGFUSE_READBACK_PAGE_LIMIT", "250")
)
LANGFUSE_READBACK_MAX_PAGES = int(
    environ.get("FLYWHEEL_LANGFUSE_READBACK_MAX_PAGES", "20")
)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_USE_SESSIONS = True
