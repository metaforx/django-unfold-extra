=========
Changelog
=========

All notable changes to django-unfold-extra are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.


Unreleased
==========

Features:
---------

* Add optional ``unfold_extra.contrib.djangocms_link`` integration: swaps the
  djangocms-link ``LinkPlugin`` for an Unfold-styled drop-in (keeps the
  ``LinkPlugin`` plugin_type), styles the link MultiWidget and attributes field
  via ``cms_widget_overrides``, and drops the redundant Delete button from the plugin
  submit row (the CMS modal already provides it). Install with the ``[link]`` extra.


0.2.9 (2026-06-17)
==================

Features:
---------

* Update django-cms to 5.0.8 and re-sync the pagetree icon font (ff5b285)

Bug Fixes:
----------

* Handle missing fields in CMS form initialization for locked URLs (d2be3de)
* Fix hint rendering for locked URL fields (cf35b8e)

Other:
------

* Update Tailwind CSS to v4.1.7 (f3fc10e)


0.2.8 (2026-05-29)
==================

Features:
---------

* Add full-width CMS modal (cf01eb4)

Bug Fixes:
----------

* Fix CMS modal breadcrumb style (0daa52b)
* Remove border radius on the text editor toolbar (8f21c29)


0.2.7 (2026-05-12)
==================

Bug Fixes:
----------

* Add inline-safe variant of ``PageSelectWidget`` to handle cloned rows (f22c19f)


0.2.6 (2026-05-11)
==================

Features:
---------

* Add Unfold objecttools buttons for versioning templates (b17f70b)

Bug Fixes:
----------

* Fix styling for django-cms versioning template confirmation actions (3a42bf2)


0.2.5 (2026-05-11)
==================

Bug Fixes:
----------

* Update styles for CMS modal breadcrumbs and editor layout (1260d25)


0.2.4 (2026-05-10)
==================

Bug Fixes:
----------

* Fix fieldset spacings in page settings (7d18bab)


0.2.3 (2026-05-10)
==================

Bug Fixes:
----------

* Prevent CMS toolbar from overlapping changelist filters (832d0b1)
* Ensure stock Site admin registers before custom unregister/re-register (a3fe7d5)


0.2.2 (2026-05-08)
==================

Features:
---------

* Add search fields (domain, name) to ``SiteAdmin`` (5db5830)

Other:
------

* Remove unused Tailwind CSS declarations from ``styles.css`` (d324734)


0.2.1 (2026-04-07)
==================

Features:
---------

* Patch the back-button template (f5ab0c9)

Other:
------

* Documentation updates for Django CMS configuration and package support


0.2.0 (2026-04-03)
==================

Other:
------

* Improve README and clarify package support; milestone release (a06575b)


0.1.14 (2026-03-31)
===================

Features:
---------

* Add django-versatileimagefield contrib integration (9fb2469)


0.1.13 (2026-03-16)
===================

Features:
---------

* Add initial test setup with models, admin, and smoke tests (1e55889)
* Migrate dependency management to Poetry (9360b03)
* Add CI workflow configuration and build badge (1384f56)
* Support CMS user settings and add Playwright frontend verification (071de00)
* Implement language synchronization between Unfold and CMS via a custom ``set_language`` view (d7e24cc)
* Add language switch with ``reload_window`` parameter for CMS sideframe support (885c26e)
* Unify the add-object location (20fb035)
* Add setting for the CMS page add button (511af83)
* Add ``UnfoldCMSPluginBase`` and demo plugin (4533228)
* Add ``PageLinkPlugin`` and support for custom widgets (Fixes #1) (b5532b4)
* Add ``DJANGOCMS_VERSIONING_ON_PUBLISH_REDIRECT`` setting (b6207c4)

Bug Fixes:
----------

* Patch Unfold's ``header_title`` to prevent admin page crashes (a55b5a6)
* Ensure Site is unregistered only if present in the registry (89de475)
* Fix font files and color configuration retrieval (8c1d15f)
* Improve CMS text plugin (tiptap) styles (Fixes #4) (4e7691b)
* Fix CMS ``UserSettings`` Unfold admin navigation and history (9038ea0)

Other:
------

* Refactor cms.pagetree styling (4b6a7b8)


0.1.11 (2026-01-31)
===================

Other:
------

* Update README for Django Unfold version and upgrade Tailwind CSS to v4.1.18 (d207c88)


0.1.10a (2025-11-08)
====================

Other:
------

* Disable source maps in the build configuration (3b634a8)


0.1.9 (2025-11-08)
==================

Bug Fixes:
----------

* Prevent sidebar content from being hidden under the django-cms topbar (e6d6f0f)

Other:
------

* Remove source-map comment from CSS (e606b3b)


0.1.8 (2025-10-16)
==================

Bug Fixes:
----------

* Support page content admin across use cases (admin / sidepanel / modal) (bec054d)
* Fix modal page content settings (7fbdef1)


0.1.7 (2025-09-29)
==================

Features:
---------

* Add theme synchronization between the iframe (Unfold) and parent window (django-cms) (8bbebc7)

Bug Fixes:
----------

* Support switching theme from CMS and Unfold simultaneously (7fb7762)
* Apply theme on page load (ade5d56)
* Conditionally unregister CMS admin models (5c2077e)


0.1.5 (2025-09-26)
==================

Features:
---------

* Integrate custom change form for Page and PageContent admins (2c1c9c8)

Bug Fixes:
----------

* Improve action buttons in ``PageContentAdmin`` (a533594)
* Fix CMS pagetree display with the Unfold sideframe (1da821b)
* Disable submit-row overwrite (64736cb)
* Fix djangocms-versioning changelist (c8301f9)
* Remove versioning breadcrumbs template (Unfold no longer uses breadcrumbs) (e87cf39)
* Fix CMS styling (sideframe, pagetree) (c710c17)


0.1.4 (2025-09-24)
==================

Other:
------

* Maintenance release (44af9d0)


0.1.3 (2025-09-24)
==================

Features:
---------

* Add djangocms-text support (c3da302)

Other:
------

* Update django-cms dependency (94b2933)


0.1.2 (2025-06-12)
==================

Features:
---------

* Initial project setup for django-unfold-extra (a62effe)
* Add View restrictions and Page permissions support (d8a3e1e)
* Add auth group defaults (ddeca8e)

Bug Fixes:
----------

* Add custom ``change_form.html`` for plugins to fix saving plugin content via modal (217a49e)
