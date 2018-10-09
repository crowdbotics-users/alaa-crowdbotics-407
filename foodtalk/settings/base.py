"""
Django settings for foodtalk project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Read .env
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get("DEBUG", "True"))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

LOCAL_APPS = ["core.api", "core.images", "core.accounts"]

THIRD_PARTY_APPS = [
    "allauth",  # registration
    "allauth.account",  # registration
    "allauth.socialaccount",  # registration
    "allauth.socialaccount.providers.facebook",  # registration
    "allauth.socialaccount.providers.instagram",  # registration
    "rest_framework",  # REST framework
    "rest_framework.authtoken",
    "taggit",  # Tags for photos
    "taggit_serializer",  # Tag serializer
    "rest_auth",  # rest auth
    "rest_auth.registration",  # enable registration
    "corsheaders",  # to accept requests from React
    "imagekit",
]

INSTALLED_APPS += LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodtalk.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "foodtalk.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = dict(
    default=dict(ENGINE="django.db.backends.sqlite3", NAME=os.path.join(BASE_DIR, "db.sqlite3"))
)
DATABASES["default"] = env.db()
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
}

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# Twilio
ACCOUNT_SECURITY_API_KEY = os.environ.get("ACCOUNT_SECURITY_API_KEY", None)

_GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', None)
if _GDAL_LIBRARY_PATH:
    GDAL_LIBRARY_PATH = _GDAL_LIBRARY_PATH

_GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH', None)
if _GEOS_LIBRARY_PATH:
    GEOS_LIBRARY_PATH = _GEOS_LIBRARY_PATH