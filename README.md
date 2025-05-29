# Django Unfold Extra

Unofficial extension for Django Unfold Admin. Adds support for django-parler and django-cms to the modern and
clean [Django Unfold](https://github.com/unfoldadmin/django-unfold) admin interface.

## Overview

Django Unfold Extra enhances the beautiful Django Unfold admin interface with additional functionality for:

- **django-parler**: Multilingual support for your Django models
- **django-cms**: Integration with Django CMS 5.0

![img.png](docs/img/cms-pagetree.png)
![img.png](docs/img/parler-tabs.png)

This package maintains the clean, modern aesthetic of Django Unfold while adding specialized interfaces for these
popular Django packages.

It uses CSS overrides where possible. As Django CMS uses many '!important' flags, I had to rebuild pagetree.css to
remove some conflicting style definitions.

> **Note:** Work in progress. Django CMS support is working but not yet fully integrated. Use at your own risk.

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
- Versioning (partial support)
- Modal support
- Not supported: Filer

Support is automatically applied. Currently, it does not support customization besides compiling your own unfold_extra
styles.

#### Frontend django CMS support

Add `unfold_extra_tags` to your base HTML template to after loading all CSS styles. This adds additional styles to hide
unfold admin like header in the django cms, for example, for page settings etc.

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
      "update:unfold": "npm run update:unfold-deps && npm run update:unfold-config",
      "tailwind:build": "npx @tailwindcss/cli -i css/unfold_extra.css -o ../static/unfold_extra/css/styles.css --minify",
      "tailwind:watch": "npx @tailwindcss/cli -i css/unfold_extra.css -o ../static/unfold_extra/css/styles.css --watch --minify"
   },
   "devDependencies": {
      "@tailwindcss/cli": "^4.1.7",
      "@tailwindcss/typography": "^0.5.16",
      "tailwindcss": "^4.1.7"
   }
}
```

#### Change colors for Django CMS

Currently, you have to manually update src/css/unfold_extra.css and compile a new styles.css extending unfold styles.

1. Fetch the latest Unfold version using `update:unfold-deps` and `update:unfold-css`
2. Update config `update:unfold`
3. Add changes `tailwind:watch` and `tailwind:build`

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
