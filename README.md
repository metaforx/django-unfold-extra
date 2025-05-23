# Django Unfold Extra

Unofficial extension for Django Unfold Admin. Adds support for django-parler and django-cms to the modern and
clean [Django Unfold](https://github.com/unfoldadmin/django-unfold) admin interface.

## Overview

Django Unfold Extra enhances the beautiful Django Unfold admin interface with additional functionality for:

- **django-parler**: Multilingual support for your Django models
- **django-cms**: Integration with Django CMS 5.0

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

- Tabs & Inlinetabs

### Versatile Image Support

- Basic support

### django-cms Support

- Theme integration in django admin (partial support in frontend)
- Pagetree
- PageUser, PageUserGroup, GlobalPagePermission
- Versioning (partial support)
- Modal support
- Not supported: Filer