# Django Unfold Extra
[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold-extra.svg?style=for-the-badge)](https://pypi.org/project/django-unfold-extra/) [![Build](https://img.shields.io/github/actions/workflow/status/metaforx/django-unfold-extra/ci.yml?style=for-the-badge&event=pull_request)](https://github.com/metaforx/django-unfold-extra/actions/workflows/ci.yml)

Unofficial extension for Django Unfold Admin. Adds support for django-cms and other common django packages to support the modern and
clean [Django Unfold](https://github.com/unfoldadmin/django-unfold) admin interface.

This package can be combined with the additional non-mandatory `Unfold Modal` package to provide a unified admin experience.
See the [django-unfold-modal](https://github.com/metaforx/django-unfold-modal) package for more details.

## Overview

Django Unfold Extra enhances the Django Unfold admin interface with additional functionality for:

- **django-cms**: Integration with Django CMS 5.0, including theme, page tree, plugins, and versioning support
- **django-parler**: Multilingual support for your Django models
- **versatile-image**: Improved integration with django-versatileimagefield, including preview and ppoi
- **Unfold auto-update**: Styles can be updated from the official Unfold package via npm
- **Theme-Sync**: Use either Unfold or Django CMS switcher to control themes. You can run both at the same time, with or without both controls enabled.

![img.png](docs/img/cms-pagetree.png)
![img.png](docs/img/parler-tabs.png)

This package maintains the clean, modern aesthetic of Django Unfold while adding specialized interfaces for these
popular Django packages.

It uses unobtrusive template and CSS-styling overrides where possible. As Django CMS uses many '!important' flags, 
pagetree.css had to be rebuilt from sources to remove some conflicting style definitions.

> **Note:** Django CMS support is not fully tested yet. Filer integration is not supported.

## Installation

1. Install the package via pip:
   ```bash
   pip install django-unfold-extra
   ```

2. Add to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
    # Unfold theme
    "unfold",
    "unfold_extra",
    # Optional integrations
    "unfold_extra.contrib.cms",
    "unfold_extra.contrib.parler",
    "unfold_extra.contrib.auth",  # you will likely want a custom auth admin
    "unfold_extra.contrib.sites",
]
```

Make sure you have already configured Django Unfold and any optional upstream packages you use
such as django CMS and django-parler.

### Configure settings

Add the following to your settings.py:

```python
from django.templatetags.static import static

UNFOLD = {
    "STYLES": [
        lambda request: static("unfold_extra/css/styles.css"),  # additional styles for supported integrations
    ],
    "SCRIPTS": [
        lambda request: static("unfold_extra/js/theme-sync.js"),  # keep django CMS theme in sync with Unfold
    ],
}
CMS_COLOR_SCHEME_TOGGLE = False  # optional: let Unfold be the single theme switch

# Move the CMS "New Page" button into Unfold's header (default: True).
# Set to False to keep the button in the CMS pagetree body.
UNFOLD_CMS_HEADER_ADD_BUTTON = True
```

### Language sync (Unfold ↔ CMS)

To keep the Unfold language switcher and the CMS toolbar/admin in sync, register
`cms_set_language` from `unfold_extra.views` as the `set_language` URL
**before** Django's i18n URLs:

```python
from unfold_extra.views import cms_set_language

urlpatterns = [
    path("i18n/setlang/", cms_set_language, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
    # ...
]
```

When a user switches language via Unfold's sidebar, `cms_set_language` updates
the CMS `UserSettings.language` before the redirect so the CMS toolbar renders
in the same language on the next request.

Add `{% unfold_extra_styles %}` and `{% unfold_extra_theme_sync %}` from `unfold_extra_tags`
to your base HTML template.
- Enables Unfold admin colors in django CMS
- Syncs the Unfold theme with django CMS (light/dark/auto)
- Adds Unfold-styled django CMS plugin admin support

### Base template integration

```html
{% load static cms_tags sekizai_tags unfold_extra_tags %}
<!DOCTYPE html>
<html>
    <head>
        <title>{% block title %}{% endblock title %}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {% render_block "css" %}
        {% unfold_extra_styles %}
        {% unfold_extra_theme_sync %}
        ...
    </head>
...
</html>
```

## Usage

### Integrations

#### django-parler Support

- UnfoldTranslatableAdminMixin
- UnfoldTranslatableStackedAdminMixin
- UnfoldTranslatableTabularAdminMixin
- TranslatableStackedInline, TranslatableTabularInline

##### Example use:

```python
class TranslatableAdmin(UnfoldTranslatableAdminMixin, BaseTranslatableAdmin):
   """custom translatable admin implementation"""

   # ... your code


class MyInlineAdmin(TranslatableStackedInline):
   model = MyModel
   tab = True  # Unfold inline settings
   extra = 0  # django inline settings
```

#### django-cms Support

- Theme integration in django admin (partial support in frontend)
- Pagetree
- PageUser, PageUserGroup, GlobalPagePermission when `CMS_PERMISSION = True`
- djangocms-versioning admin template and styling support
- CMS UserSettings singleton admin navigation and submit row
- "New Page" button in Unfold header position (configurable via `UNFOLD_CMS_HEADER_ADD_BUTTON`)
- Modal support
- Not supported: Filer

Support is automatically applied. Currently, it does not support customization besides compiling your own unfold_extra
styles.

##### CMS Plugins with Unfold styling

For the general django CMS plugin model, see the official guide:
https://docs.django-cms.org/en/stable/how_to/09-custom_plugins.html

This package only changes the admin side:
- use `UnfoldCMSPluginBase` instead of `CMSPluginBase`
- use `UnfoldStackedInline` or `UnfoldTabularInline` for plugin inlines


```python
# cms_plugins.py
from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase
from .models import HeroPluginModel

@plugin_pool.register_plugin
class HeroPlugin(UnfoldCMSPluginBase):
    model = HeroPluginModel
    name = _("Hero")
    render_template = "plugins/hero.html"
```

Most Unfold/Django admin edit options also work on plugins, including
`compressed_fields`, `fieldsets`, `readonly_fields`, `autocomplete_fields`,
`raw_id_fields` lookup popups, `radio_fields`, and `formfield_overrides`.

Use `cms_widget_overrides` when you need to replace plugin form widgets that
should use Unfold-compatible widgets:

```python
from unfold_extra.contrib.cms.plugins import UnfoldCMSPluginBase


class MyPlugin(UnfoldCMSPluginBase):
    cms_widget_overrides = {
        **UnfoldCMSPluginBase.cms_widget_overrides,
        SomeField: MyCustomWidget,
    }
```

See Unfold docs:
- https://unfoldadmin.com/docs/configuration/modeladmin/
- https://unfoldadmin.com/docs/tabs/fieldsets/

##### Frontend django CMS support

Add `unfold_extra_tags` to your base HTML template after loading all CSS styles.
This adds additional styles to integrate django CMS with Unfold Admin and exposes `"COLORS"` from Unfold settings on
the public website for authenticated django-cms admin users.

```html
{% load cms_tags sekizai_tags unfold_extra_tags %}
<head>
   ...
   {% render_block "css" %}
   {% unfold_extra_styles %}
   ...
</head>
```

##### Custom compilation via npm/pnpm

The current frontend scripts live in `unfold_extra/src/package.json`. Run them from
`unfold_extra/src`, for example:

```bash
npm run update:unfold
npm run tailwind:build
npm run tailwind:watch
npm run build:js
```

##### Sync CMS pagetree CSS after upgrading django-cms

The CMS pagetree CSS is vendored with Unfold compatibility patches (e.g. removing the bare `.hidden` selector
that conflicts with Tailwind/Unfold sidebar). After upgrading django-cms, re-sync the patched CSS:

```bash
poetry run python scripts/sync_cms_pagetree.py
```

The script will warn if any patch targets have changed upstream and need manual review.

##### Change colors for Django CMS

Configure colors through Unfold in `settings.py` using `UNFOLD["COLORS"]`.
This is the minimal and recommended way to align the admin theme, including the
shared base, primary, and font colors used by this package.

```python
UNFOLD = {
    "COLORS": {
        "base": {
            "50": "oklch(98.5% 0.002 247.839)",
            "100": "oklch(96.7% 0.003 264.542)",
            "200": "oklch(92.8% 0.006 264.531)",
            "300": "oklch(87.2% 0.009 258.338)",
            "400": "oklch(71.4% 0.019 261.325)",
            "500": "oklch(55.1% 0.023 264.364)",
            "600": "oklch(44.6% 0.026 256.802)",
            "700": "oklch(37.3% 0.031 259.733)",
            "800": "oklch(27.8% 0.030 256.848)",
            "900": "oklch(21.0% 0.032 264.665)",
            "950": "oklch(13.0% 0.027 261.692)",
        },
        "primary": {
            "50": "oklch(97.7% 0.014 308.299)",
            "100": "oklch(94.6% 0.033 307.174)",
            "200": "oklch(90.2% 0.060 306.703)",
            "300": "oklch(82.7% 0.108 306.383)",
            "400": "oklch(72.2% 0.177 305.504)",
            "500": "oklch(62.7% 0.233 303.900)",
            "600": "oklch(55.8% 0.252 302.321)",
            "700": "oklch(49.6% 0.237 301.924)",
            "800": "oklch(43.8% 0.198 303.724)",
            "900": "oklch(38.1% 0.166 304.987)",
            "950": "oklch(29.1% 0.143 302.717)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
}
```

For CMS-specific theme adjustments beyond the shared Unfold palette, update the
frontend assets in `unfold_extra/src`.

See the official Unfold docs:
- Settings options: https://unfoldadmin.com/docs/configuration/settings/
- Customizing Tailwind stylesheet: https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/


#### Versatile Image Support

- Improved unfold integration via CSS only.

#### Django Auth, Sites

- Adds Unfold-based admin registrations for `django.contrib.auth` and `django.contrib.sites`.

This is for personal use. You likely want to customize this. 
