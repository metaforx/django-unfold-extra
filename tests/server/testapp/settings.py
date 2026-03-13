from os import environ
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.templatetags.static import static

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

USE_TZ = True

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
    # Django CMS plugins
    # Parler
    "parler",
    # Test app
    "testapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
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

# Django CMS settings
CMS_TEMPLATES = [
    ("base.html", "Base"),
]

CMS_CONFIRM_VERSION4 = True
CMS_PERMISSION = False
CMS_COLOR_SCHEME_TOGGLE = False

LANGUAGES = [
    ("en", "English"),
    ("de", "German"),
]
LANGUAGE_CODE = "en"

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

# Unfold settings
UNFOLD = {
    "STYLES": [
        lambda request: static("unfold_extra/css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("unfold_extra/js/theme-sync.js"),
    ],
}

X_FRAME_OPTIONS = "SAMEORIGIN"
