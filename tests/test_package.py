"""Tests for unfold_extra package imports and configuration."""


class TestPackageImport:
    """Verify package can be imported and has expected attributes."""

    def test_import_package(self):
        import unfold_extra

        assert hasattr(unfold_extra, "__version__")

    def test_import_app_config(self):
        from unfold_extra.apps import UnfoldCMSConfig

        assert UnfoldCMSConfig.name == "unfold_extra"

    def test_import_template_tags(self):
        from unfold_extra.templatetags import unfold_extra_tags

        assert hasattr(unfold_extra_tags, "unfold_theme_colors")
        assert hasattr(unfold_extra_tags, "unfold_extra_styles")
        assert hasattr(unfold_extra_tags, "unfold_extra_theme_sync")

    def test_import_parler_admin(self):
        from unfold_extra.contrib.parler.admin import UnfoldTranslatableAdminMixin

        assert UnfoldTranslatableAdminMixin is not None

    def test_import_cms_admin(self):
        from unfold_extra.contrib.cms.admin import PageContentAdmin, PageAdmin

        assert PageContentAdmin is not None
        assert PageAdmin is not None
