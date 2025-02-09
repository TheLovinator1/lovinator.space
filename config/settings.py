from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from platformdirs import user_data_dir

logger: logging.Logger = logging.getLogger(__name__)

load_dotenv(verbose=True)
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

if not DEBUG:
    import sentry_sdk

    sentry_sdk.init(
        dsn="https://a1def3e5323ad037cfab2c82bcb6e94e@o4505228040339456.ingest.us.sentry.io/4508790769713152",
        send_default_pii=True,
        traces_sample_rate=1.0,
        _experiments={"continuous_profiling_auto_start": True},
    )
else:
    logger.debug("Debug mode is enabled. Sentry SDK will not be initialized.")

BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = Path(
    user_data_dir(
        appname="lovinator.space",
        appauthor="TheLovinator",
        roaming=True,
        ensure_exists=True,
    ),
)


SECRET_KEY: str | None = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    msg = "DJANGO_SECRET_KEY environment variable is not set."
    raise ValueError(msg)


WSGI_APPLICATION: str = "config.wsgi.application"
ALLOWED_HOSTS: list[str] = [] if DEBUG else [".lovinator.space"]
INTERNAL_IPS: list[str] = ["127.0.0.1", "::1"]
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = " "

ROOT_URLCONF: str = "config.urls"
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

TIME_ZONE: str = "Europe/Stockholm"
USE_I18N: bool = False

STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

ADMINS: list[tuple[str, str]] = [("Joakim Hellsén", "tlovinator@gmail.com")]

# Site ID is used by the sites framework
SITE_ID: int = 1

# Email settings
EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: str = "smtp.gmail.com"
EMAIL_PORT: int = 587
EMAIL_USE_TLS: bool = True
EMAIL_HOST_USER: str | None = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD: str | None = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_SUBJECT_PREFIX: str = "[lovinator.space] "
EMAIL_USE_LOCALTIME = True
EMAIL_TIMEOUT: int = 10
DEFAULT_FROM_EMAIL: str = os.getenv("EMAIL_HOST_USER", "webmaster@localhost")
SERVER_EMAIL: str = os.getenv("EMAIL_HOST_USER", "webmaster@localhost")


INSTALLED_APPS: list[str] = [
    # Django apps
    "django.contrib.contenttypes",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    # Local apps
    "core.apps.CoreConfig",
]

MIDDLEWARE: list[str] = ["django.middleware.common.CommonMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware"]


TEMPLATES: list[dict[str, str | bool | dict[str, list[str]] | list[str]]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]


DATABASES: dict[str, dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "lovinator_space.sqlite3",
        "OPTIONS": {
            "init_command": "PRAGMA journal_mode=wal; PRAGMA synchronous=1; PRAGMA mmap_size=134217728; PRAGMA journal_size_limit=67108864; PRAGMA cache_size=2000;",  # noqa: E501
        },
    },
}

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "asyncio": {  # Hide "Using selector: SelectSelector" spam
            "level": "WARNING",
        },
    },
}

STORAGES = {
    "default": {
        "ENGINE": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": DATA_DIR / "media",
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
