from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_MODE = os.getenv("ENV_MODE", "dev").lower()

def _load_dotenv_if_needed():
    if ENV_MODE in ("local", "dev"):
        env_path = BASE_DIR / "secrets" / f".env.{ENV_MODE}"
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except Exception:
                pass

_load_dotenv_if_needed()

def get_bool(name, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

def get_int(name, default):
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default

def get_list(name, default=None, sep=","):
    if default is None:
        default = []
    v = os.getenv(name)
    if not v:
        return default
    return [x.strip() for x in v.split(sep) if x.strip()]

# =======================
# Security / Core
# =======================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set")

DEBUG = get_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = get_list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"]
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_HTTPS = get_bool("USE_HTTPS", default=(ENV_MODE == "prod"))

# =======================
# Applications
# =======================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    "accounts.apps.AccountConfig",
    "points.apps.PointConfig",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=get_int("JWT_ACCESS_MIN", 25)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=get_int("JWT_REFRESH_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),

    "AUTH_COOKIE": os.getenv("AUTH_COOKIE", "access_token"),
    "AUTH_COOKIE_SECURE": get_bool("COOKIE_SECURE", default=USE_HTTPS),
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": os.getenv("COOKIE_SAMESITE", "Lax"),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crowdfund_project.urls"
WSGI_APPLICATION = "crowdfund_project.wsgi.application"

TEMPLATES = [{
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
}]

# =======================
# CORS / CSRF
# =======================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = get_list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = get_list("CSRF_TRUSTED_ORIGINS", default=[])

SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_HTTPONLY = get_bool("CSRF_COOKIE_HTTPONLY", default=False)

# =======================
# Database
# =======================
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

if DB_ENGINE == "mysql":
    if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
        raise ValueError("MySQL settings are incomplete")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT or "3306",
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =======================
# Static / Media
# =======================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =======================
# Security Headers
# =======================
if ENV_MODE == "prod":
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

# =======================
# Logging
# =======================
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

AUTH_USER_MODEL = "accounts.User"
