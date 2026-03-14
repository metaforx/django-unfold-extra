from os import environ
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

USE_TZ = True
USE_I18N = True

INSTALLED_APPS = [
    # Unfold must come before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold_extra",
    "unfold_extra.contrib.cms",
    "unfold_extra.contrib.parler",
    "unfold_extra.contrib.auth",
    "unfold_extra.contrib.sites",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Django CMS core
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    # Django CMS versioning
    "djangocms_versioning",
    # Parler
    "parler",
    # Test app
    "testapp",
]

MIDDLEWARE = [
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

ROOT_URLCONF = "testapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "testapp" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django sites framework
SITE_ID = 1

# --- Language / i18n ---
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]

# CMS language configuration (keyed by SITE_ID)
# https://docs.django-cms.org/en/latest/topics/i18n.html
CMS_LANGUAGES = {
    SITE_ID: [
        {
            "code": "en",
            "name": _("English"),
            "public": True,
        },
        {
            "code": "de",
            "name": _("Deutsch"),
            "public": True,
            "hide_untranslated": True,
        },
    ],
    "default": {
        "fallbacks": ["en"],
        "redirect_on_fallback": True,
        "public": True,
        "hide_untranslated": False,
    },
}

# Parler settings
PARLER_LANGUAGES = {
    SITE_ID: (
        {"code": "en"},
        {"code": "de"},
    ),
    "default": {
        "fallbacks": ["en"],
        "hide_untranslated": False,
    },
}

# --- Django CMS ---
CMS_TEMPLATES = [
    ("base.html", "Base"),
]

CMS_CONFIRM_VERSION4 = True
CMS_PERMISSION = False
CMS_COLOR_SCHEME_TOGGLE = False

# djangocms-versioning: default user for programmatic version creation (tests/fixtures)
DJANGOCMS_VERSIONING_DEFAULT_USER = 1

# --- Unfold ---
UNFOLD = {
    "SHOW_LANGUAGES": True,
    "STYLES": [
        lambda request: static("unfold_extra/css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("unfold_extra/js/theme-sync.js"),
    ],
}

X_FRAME_OPTIONS = "SAMEORIGIN"
