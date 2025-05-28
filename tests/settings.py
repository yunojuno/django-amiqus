from os import path

from django.core.exceptions import ImproperlyConfigured

DEBUG = True
TEMPLATE_DEBUG = True
USE_TZ = True


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "amiqus.db"}}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "amiqus",
    "tests.test_app",
)

MIDDLEWARE = [
    # default django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

PROJECT_DIR = path.abspath(path.join(path.dirname(__file__)))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
            ]
        },
    }
]

AUTH_USER_MODEL = "test_app.User"

STATIC_URL = "/static/"

SECRET_KEY = "amiqus"  # noqa: S105

ALLOWED_HOSTS = [
    "127.0.0.1",
    ".ngrok.io",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {"handlers": ["console"], "propagate": True, "level": "DEBUG"},
        "amiqus": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

ROOT_URLCONF = "tests.urls"

if not DEBUG:
    raise ImproperlyConfigured("This settings file can only be used with DEBUG=True")
