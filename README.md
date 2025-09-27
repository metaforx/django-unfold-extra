# Django Unfold Extra

Unofficial extension for Django Unfold Admin. Adds support for django-parler and django-cms to the modern and
clean [Django Unfold](https://github.com/unfoldadmin/django-unfold) admin interface.

## Overview

Django Unfold Extra enhances the beautiful Django Unfold admin interface (v.0.66.0) with additional functionality for:

- **django-cms**: Integration with Django CMS 5.0 - Uses unfold admin colors for django cms
- **django-parler**: Multilingual support for your Django models
- **versatile-image**: Improved integration with django-versatileimagefield, including preview and ppoi
- **Unfold auto-update**: Styles can be automatically updaten from official unfold package via npm
- **Theme-Sync**: Use either Unfold or Django CMS switcher to control themes. You can run both at the same time, with or without both controls enabled.

![img.png](docs/img/cms-pagetree.png)
![img.png](docs/img/parler-tabs.png)

This package maintains the clean, modern aesthetic of Django Unfold while adding specialized interfaces for these
popular Django packages.

It uses unobtrusive template and CSS-styling overrides where possible. As Django CMS uses many '!important' flags, 
pagetree.css had to be rebuilt from sources to remove some conflicting style definitions.

> **Note:** Django CMS support is not fully tested, but all features should work, beside filer. 

## Installation

1. Install the package via pip:
   ```bash
   pip install django-unfold-extra
   ```

2. Add to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
   # Unfold theme
   'unfold',
   'unfold_extra',
   'unfold_extra.contrib.cms',  # if extra packages
   'unfold_extra.contrib.parler',
   'unfold_extra.contrib.auth'  # you likely want to use your own implementation
   'unfold_extra.contrib.sites'

   # Your apps
   # ...
]
```

Make sure you've set up Django Unfold according to its documentation.
https://github.com/unfoldadmin/django-unfold

Add the following to your settings.py:

```python
from django.templatetags.static import static

UNFOLD = {
    "STYLES": [
        lambda request: static("unfold_extra/css/styles.css"), # additional styles for 3rd party packages
    ],
    "SCRIPTS": [
        lambda request: static("unfold_extra/js/theme-sync.js"), # switch django cms theme from "Unfold Admin"
    ],
}
CMS_COLOR_SCHEME_TOGGLE = False # disable django cms theme switch -> use Unfold admin theme switch or disable Unfold theme switch via styles, no config option yet.
```

Add `{% unfold_extra_styles %}` and `{% unfold_extra_theme_receiver %}`  from `unfold_extra_tags` to your base HTML template. 
- Enables unfold admin colors in django cms
- theme switch from unfold admin to change theme in djangs cms (light/dark/auto)

```html
{% load static cms_tags sekizai_tags unfold_extra_tags%}
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

### django-parler Support

- UnfoldTranslatableAdminMixin
- UnfoldTranslatableStackedAdminMixin
- UnfoldTranslatableTabularAdminMixin
- TranslatableStackedInline, TranslatableTabularInline

#### Example use:

```python
class TranslatableAdmin(UnfoldTranslatableAdminMixin, BaseTranslatableAdmin):
   """custom translatable admin implementation"""

   # ... your code


class MyInlineAdmin(TranslatableStackedInline):
   model = MyModel
   tab = True  # Unfold inline settings
   extra = 0  # django inline settings
```

### django-cms Support

- Theme integration in django admin (partial support in frontend)
- Pagetree
- PageUser, PageUserGroup, GlobalPagePermission
- Versioning
- Modal support
- Not supported: Filer

Support is automatically applied. Currently, it does not support customization besides compiling your own unfold_extra
styles.

#### Frontend django CMS support

Add `unfold_extra_tags` to your base HTML template to after loading all CSS styles. 
This adds additional styles to integrate django CMS with Unfold Admin and includes `"COLORS"` from unfold settings to 
the public website for authenticated django-cms admin users.

```html
{% load cms_tags sekizai_tags unfold_extra_tags%}
<head>
   ...
   {% render_block "css" %}
   {% unfold_extra_styles %}
   ...
</head>
```

#### Custom compilation via npm/pnpm (see src/package.json)

```json
{
	"name": "django-unfold-extra",
	"description": "Enhancing Django Unfold to support additional packages",
	"scripts": {
		"update:unfold-deps": "curl -s https://raw.githubusercontent.com/unfoldadmin/django-unfold/main/package.json | jq -r '[\"tailwindcss@\" + .dependencies.tailwindcss, \"@tailwindcss/typography@\" + .devDependencies[\"@tailwindcss/typography\"]] | join(\" \")' | xargs npm install --save-dev",
		"update:unfold-css": "curl -o css/styles.css https://raw.githubusercontent.com/unfoldadmin/django-unfold/main/src/unfold/styles.css",
		"update:unfold": "npm run update:unfold-deps && npm run update:unfold-css",
		"tailwind:build": "npx @tailwindcss/cli -i css/unfold_extra.css -o ../static/unfold_extra/css/styles.css --minify",
		"tailwind:watch": "npx @tailwindcss/cli -i css/unfold_extra.css -o ../static/unfold_extra/css/styles.css --watch --minify"
	},
	"devDependencies": {
		"@tailwindcss/cli": "^4.1.7",
		"@tailwindcss/typography": "^0.5.19",
		"tailwindcss": "^4.1.13"
	}
}
```

#### Change colors for Django CMS

You can change the colors for django CMS by editing `css/unfold_extra.css` or just update the unfold colors via settings.py.

1. Fetch the latest Unfold version using `update:unfold-deps` and `update:unfold-css`
2. Update config `update:unfold`
3. Add changes `tailwind:watch` and `tailwind:build

```css
html:root {
   --dca-light-mode: 1;
   --dca-dark-mode: 0;
   --dca-white: theme('colors.white');
   --dca-black: theme('colors.black');
   --dca-shadow: theme('colors.base.950');
   --dca-primary: theme('colors.primary.600');
   --dca-gray: theme('colors.base.500');
   --dca-gray-lightest: theme('colors.base.100');
   --dca-gray-lighter: theme('colors.base.200');
   --dca-gray-light: theme('colors.base.400');
   --dca-gray-darker: theme('colors.base.700');
   --dca-gray-darkest: theme('colors.base.800');
   --dca-gray-super-lightest: theme('colors.base.50');

   --active-brightness: 0.9;
   --focus-brightness: 0.95;
}


html.dark {
   --dca-light-mode: 0;
   --dca-dark-mode: 1;
   --dca-white: theme('colors.base.900');
   --dca-black: theme('colors.white');
   --dca-primary: theme('colors.primary.500');
   --dca-gray: theme('colors.base.300') !important;
   --dca-gray-lightest: theme('colors.base.700');
   --dca-gray-lighter: theme('colors.base.600');
   --dca-gray-light: theme('colors.base.400');
   --dca-gray-darker: theme('colors.base.200');
   --dca-gray-darkest: theme('colors.base.100');
   --dca-gray-super-lightest: theme('colors.base.800');

   --active-brightness: 2;
   --focus-brightness: 1.5;
}
```


### Versatile Image Support

- Improved unfold integration via CSS only.

### Django Auth, Sites

- Add Unfolds standard settings to `django.contrib.auth`,`django.contrib.sites`.

This is for personal use. You likely want to customize this. 
