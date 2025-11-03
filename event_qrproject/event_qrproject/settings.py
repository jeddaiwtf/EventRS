# settings.py

import os
from pathlib import Path

# ------------------------------------------------------------------
# Base directory of your Django project
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-defaultkeyfor-dev-only-1234567890')

# ------------------------------------------------------------------
# SECURITY WARNING: don't run with debug turned on in production!
# ------------------------------------------------------------------
DEBUG = True  # ✅ Turn this ON during development. Set to False when deploying.

# ------------------------------------------------------------------
# Allowed hosts — include localhost + ngrok during dev
# ------------------------------------------------------------------
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "refractorily-catabatic-shirleen.ngrok-free.dev",  # your ngrok domain
]

# ------------------------------------------------------------------
# Installed apps (make sure 'tickets' is here)
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "tickets",
    # Add other apps if you have them
]

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------------
# Root URL configuration
# ------------------------------------------------------------------
ROOT_URLCONF = "event_qrproject.urls"

# ------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------------
# WSGI
# ------------------------------------------------------------------
WSGI_APPLICATION = "event_qrproject.wsgi.application"

# ------------------------------------------------------------------
# Database (default: SQLite)
# ------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Static and Media Files
# ------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # ✅ make sure /static folder exists
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------------
# Base Public URL for generating external links / QR (used with ngrok)
# ------------------------------------------------------------------
BASE_URL = "https://refractorily-catabatic-shirleen.ngrok-free.dev"
 # Example: https://abcd1234.ngrok-free.app

# ------------------------------------------------------------------
# Default primary key field type
# ------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
