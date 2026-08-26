/**
 * Unfold Extra - filer popup links
 *
 * filer's "New Folder" button calls Django's showAddAnotherPopup() straight from
 * an inline onclick. Django's own popup links do not: they carry
 * `.related-widget-wrapper-link[data-popup="yes"]`, and the delegated handler
 * behind that selector fires a `django:show-related` event before falling back to
 * window.open(). That event is what anything replacing admin popups listens for —
 * django-unfold-modal opens its modal from it — so filer's shortcut is invisible
 * to all of it.
 *
 * Restating the link the way the admin states its own puts it back on that path.
 * With nothing listening, the fallback opens the very same popup window as before.
 */
'use strict';

(function () {
    function popupName(link) {
        // Django and the modal both name the popup after the link's id, minus the
        // `add_` prefix.
        return link.id || 'add_folder';
    }

    function handleClick(event) {
        const link = event.currentTarget;

        event.preventDefault();

        // filer's base_site.html loads RelatedObjectLookups.js on top of the admin
        // media that already carries it, so its delegated click handler is bound
        // twice — and two handlers would mean two popups. Keep the click here and
        // announce it once ourselves.
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

            if (!link.id) link.id = popupName(link);

            link.addEventListener('click', handleClick);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
