from django.apps import AppConfig


class CmsConfig(AppConfig):
    name = "unfold_extra.contrib.cms"
    label = "unfold_extra_cms"

    def ready(self):
        from unfold_extra.contrib.cms.unfold_patches import patch_unfold_header_title

        patch_unfold_header_title()
