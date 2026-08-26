=========
Changelog
=========

All notable changes to django-unfold-extra are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.


Unreleased
==========

Bug Fixes:
----------

* Give filer's "New Folder" popup the Unfold layout, matching the copy/move/rename
  confirmation dialogs, and make its cancel button reliably close the popup.

0.5.0 (2026-08-26)
==================

Features:
---------

* Add ``unfold_extra.contrib.filer`` integration: re-registers django-filer's
  ``Folder``, ``File``, ``Clipboard``, ``Image``, ``FolderPermission`` and
  ``ThumbnailOption`` admins with Unfold styling. ``django-filer`` is an optional
  dependency — install with ``pip install django-unfold-extra[filer]``.
* Ship a Unfold-patched copy of filer's ``admin_filer.css`` (vendored by
  ``scripts/sync_filer_css.py``) that removes the bare ``.hidden`` rule colliding
  with the Unfold sidebar, drops a global ``height:100% !important`` rule, and
  re-scopes ``.filebrowser h2{display:none}`` to ``#content`` so the folder
  directory-listing view no longer hides the Unfold sidebar navigation titles
  (which left the sidebar looking empty). It shadows filer's own
  ``filer/css/admin_filer.css`` static path so every filer admin template (folder
  listing, change forms, delete and move/copy dialogs) loads the patched CSS
  without per-template overrides.
* Fix ``KeyError: 'add'`` when adding a folder: filer's "make folder" popup is
  served by a custom view without the standard admin context, while Unfold's
  ``change_form.html`` renders ``{% submit_row %}`` in the footer (outside the
  content block). The contrib.filer override of ``new_folder_form.html`` blanks
  that block and renders its own Unfold-styled Save button.
* Restore the filer file/image change-form UI under Unfold:

  - Render filer's native image preview + focal-point (subject location) picker,
    which lived in ``{% block object-tools %}`` — a block Unfold's change_form does
    not output — by relocating filer's ``detail_info`` panel into a rendered block.
  - Apply Unfold's styled file widget to filer's ``file`` field (filer hard-codes a
    bare ``FileInput``).
  - Re-target Unfold's header breadcrumb to filer's folder navigation
    (Filer -> root folder -> ancestor folders -> object) instead of the flat
    app/model/object trail, keeping Unfold's native header styling and back button.
  - Render the read-only canonical URL as a visible Unfold-styled link.

* Give filer's folder directory-listing views a proper Unfold header. The listing
  is a folder tree rather than a model changelist, so its context has no ``opts``
  or ``cl`` and Unfold's ``{% header_title %}`` fell back to ``content_title`` —
  which filer sets to a literal ``<h2>&nbsp;</h2>`` spacer, leaving an empty
  heading with no navigation. ``FolderAdmin.directory_listing_template`` now points
  at an override that renders Unfold's header with filer's folder trail
  (Filer -> Folder -> ancestor folders -> current folder), preserving filer's popup
  URL parameters. The change-form breadcrumb was refactored onto the same shared
  header/breadcrumb includes.
* Style filer's navigator search box to match the CMS pagetree search — filer
  rendered it as a bare, borderless 12px field next to a solid primary button.
  Both are now driven by one shared rule so they cannot drift apart.
* Replace filer's blue folder icons with Material Symbols glyphs (outlined, 24dp
  — the same family Unfold uses): ``folder``, ``folder_special`` for the root
  crumb, ``folder_open`` for unfiled uploads and ``file_open`` for the navigator
  dropdown. Each is tinted with the project's ``--color-primary-600`` token
  rather than a baked hex, and shadows filer's own static path so every filer
  template picks it up without overrides. filer's ``file-*`` type icons are
  unchanged — they are multi-tone illustrations, not glyphs.
* Fix selection and bulk actions on filer's directory listing. Unfold ships an
  ``admin/js/actions.js`` that shadows Django's and binds only to Unfold's own
  changelist markup, so on filer's stock markup nothing bound: the "N of M
  selected" counter never moved, table rows never got the ``selected`` class, and
  filer's toolbar copy/move/delete buttons — which are inert without it — did
  nothing in table view. contrib.filer now ships a small script that restores the
  wiring for both list types, updates every counter on the page (filer renders
  two) and cascades the select-all toggles, including the thumbnail view's
  per-section "all folders" / "all files" toggles.
* Frame filer's directory listing as a bordered card so the list view matches
  Unfold's detail views. filer renders its toolbar and table as two flush,
  unframed siblings; the border, radius and shadow go on their shared
  ``#content`` parent, scoped by the ``filebrowser`` body class. Unlike Unfold's
  fieldset module it mimics, the frame omits ``overflow: hidden`` — filer's
  toolbar dropdowns overflow a short listing by design and would be clipped.
* Keep the folder breadcrumb off filer's non-file models. Django resolves
  ``admin/filer/change_form.html`` for every model in the ``filer`` app label, so
  the folder trail placed there also hit ``Clipboard``, ``FolderPermission`` and
  ``ThumbnailOption`` — a thumbnail option rendered as "Filer -> Folder -> big".
  The trail now lives in the file/image change-form templates, and those models
  keep Unfold's default app/model/object trail.
* Lay filer's file/image picker widget out in flow. Its stylesheet positions the
  widget's contents absolutely inside a fixed-height box under a scope Unfold also
  renders (``form .form-row``), so the file name, buttons and drop preview spilled
  over the next field and swallowed its clicks. Unfold's related-widget menu is
  hidden alongside: its links only work on ``<select>`` widgets, and filer ships
  its own choose/edit/clear controls.
* Render filer's copy, move, rename, resize and delete-selected confirmation pages
  as Unfold cards, with Unfold widgets on the forms behind them.

Changed:
--------

* Require ``django-cms>=5.0.9``: it pads ``.cms-sideframe-frame`` by the toolbar
  height itself, so unfold_extra's own offset was dropped (it doubled the gap,
  and the sidebar rule was never scoped to the sideframe).


0.4.0 (2026-07-27)
==================

Features:
---------

* Add optional ``unfold_extra.contrib.djangocms_alias`` integration: Unfold-styled
  ``Alias``, ``AliasContent`` and ``Category`` admin, an Unfold-styled Alias plugin
  form and "Create Alias" popup, and the alias usage / delete listings rendered
  through Unfold's table component
* ``UnfoldCMSPluginBase`` now also restyles widgets on fields declared directly on a
  plugin form (``render_change_form``), covering views that build their own form

Bug Fixes:
----------

* Stop ``UnfoldCMSPluginBase`` shadowing a plugin's ``name`` and ``form``: the django CMS
  metaclass stamps both onto every subclass, including the base
* Load django CMS' own ``cms.pagetree.css`` again and layer a small override on top,
  replacing the vendored copy and its sync script


0.3.0 (2026-07-27)
==================

Breaking Changes:
-----------------

* Require Python >=3.12; drop support for 3.9 / 3.10 / 3.11 (required by django-unfold >=0.92)
* Require django-unfold >=0.92 for the reworked ``unfold.mixins`` API; ``UnfoldCMSPluginBase`` now composes ``FormFieldModelAdminMixin``, ``ActionModelAdminMixin``, ``DatasetModelAdminMixin`` and ``NestedInlinesModelAdminMixin`` (previously the removed ``BaseModelAdminMixin``)

Features:
---------

* Add optional ``unfold_extra.contrib.djangocms_link`` integration: swaps the
  djangocms-link ``LinkPlugin`` for an Unfold-styled drop-in (keeps the
  ``LinkPlugin`` plugin_type), styles the link MultiWidget and attributes field
  via ``cms_widget_overrides``, and drops the redundant Delete button from the plugin
  submit row (the CMS modal already provides it). Install with the ``[link]`` extra.

Other:
------

* Migrate dependency management from Poetry to uv
* Restore djangocms-versioning to the test dependency group
* Update CI to run on uv with a Python 3.12 / 3.13 matrix


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
