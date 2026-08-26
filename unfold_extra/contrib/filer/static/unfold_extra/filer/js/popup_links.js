/**
 * Unfold Extra - filer popup links
 *
 * filer's "New Folder" button calls showAddAnotherPopup() from an inline onclick,
 * so it never fires the `django:show-related` event a modal replacement listens
 * for. Restate it as an admin popup link and announce the click once; with
 * nothing listening, the fallback opens the same popup window as before.
 */
'use strict';

(function () {
    function handleClick(event) {
        const link = event.currentTarget;

        event.preventDefault();

        // filer's base_site.html loads RelatedObjectLookups.js on top of the admin
        // media, binding its delegated handler twice — two handlers, two popups.
        event.stopPropagation();

        const jQuery = typeof django !== 'undefined' && django.jQuery;

        if (!jQuery) {
            window.showAddAnotherPopup(link);
            return;
        }

        const showRelated = jQuery.Event('django:show-related', { href: link.href });

        jQuery(link).trigger(showRelated);

        if (!showRelated.isDefaultPrevented()) {
            window.showRelatedObjectPopup(link);
        }
    }

    function init() {
        document.querySelectorAll('a[onclick*="showAddAnotherPopup"]').forEach(function (link) {
            link.removeAttribute('onclick');
            link.classList.add('related-widget-wrapper-link');
            link.dataset.popup = 'yes';

            // Django and the modal name the popup after the link's id.
            if (!link.id) link.id = 'add_folder';

            link.addEventListener('click', handleClick);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
