from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# =======================
# Base Directory
# =======================
BASE_DIR = Path(__file__).resolve().parent.parent


# ===========================
# Load Environment by MODE
# ===========================
ENV_MODE = os.getenv("ENV_MODE", "dev")   # ← デフォルトは dev

ENV_PATH = BASE_DIR / "secrets" / f".env.{ENV_MODE}"
load_dotenv(ENV_PATH)

print(f"Using env file: {ENV_PATH}")  # デバッグ用（後で削除OK）

# =======================
# Security
# =======================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in secrets/.env")

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# =======================
# Application definition
# =======================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",

    "accounts.apps.AccountConfig",
    "points.apps.PointConfig",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.authentication.CookieJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

# =======================
# JWT Settings
# =======================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MIN", 25))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", 7))),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_SECURE": os.getenv("COOKIE_SECURE", "False").lower() == "true",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": os.getenv("COOKIE_SAMESITE", "Lax"),
}

# =======================
# Middleware
# =======================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crowdfund_project.urls"

# =======================
# Templates
# =======================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crowdfund_project.wsgi.application"

# =======================
# CORS Settings
# =======================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# =======================
# Database
# =======================
if os.getenv("DB_ENGINE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:  # ローカル開発は SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =======================
# Password validation
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =======================
# Internationalization
# =======================
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"

USE_I18N = True
USE_TZ = True

# =======================
# Static / Media
# =======================
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =======================
# Custom User
# =======================
AUTH_USER_MODEL = "accounts.User"
