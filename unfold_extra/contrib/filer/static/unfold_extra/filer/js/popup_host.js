/**
 * Unfold Extra - filer popup host
 *
 * filer's popups (New Folder, the file/folder pickers) were written for
 * window.open(): they talk back through `window.opener`. Opened inside an Unfold
 * modal — django-unfold-modal renders the same URL in an iframe — there is no
 * opener, and the calls blow up. This exposes the one thing those pages need to
 * know: the modal that is hosting them, if any.
 *
 * Returns django-unfold-modal's API object (`close()`, `open()`) on the parent
 * window, or null when the page stands on its own — in a real popup window, in
 * the CMS sideframe, or with django-unfold-modal simply not installed.
 */
'use strict';

window.unfoldExtraFilerModal = function () {
    try {
        const frame = window.frameElement;

        if (window.parent === window || !frame) return null;
        if (!frame.classList.contains('unfold-modal-iframe')) return null;

        return window.parent.UnfoldModal || null;
    } catch (e) {
        // Cross-origin parent: not our modal.
        return null;
    }
};
