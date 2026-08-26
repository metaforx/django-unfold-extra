/**
 * Unfold Extra - filer popup host
 *
 * filer's popups report back through `window.opener`, which an Unfold modal
 * iframe does not have. Resolves whichever one is hosting the page — popup
 * window or modal — so filer's pages can close and refresh it either way, and
 * wires the cancel links to it.
 */
'use strict';

window.UnfoldExtraFilerPopup = window.UnfoldExtraFilerPopup || {};

(function (Popup) {
    function opener() {
        return window.opener && !window.opener.closed ? window.opener : null;
    }

    function modal() {
        try {
            const frame = window.frameElement;

            if (window.parent === window || !frame) return null;
            if (!frame.classList.contains('unfold-modal-iframe')) return null;

            return window.parent.UnfoldModal || null;
        } catch (e) {
            return null;
        }
    }

    function close() {
        const host = modal();

        if (opener()) {
            window.close();
        } else if (host) {
            host.close();
        } else {
            window.history.back();
        }
    }

    function reloadHost() {
        if (opener()) {
            opener().dismissPopupAndReload(window);
        } else if (modal()) {
            // Reloading the page behind the modal takes the modal with it.
            window.parent.location.reload();
        }
    }

    function wireCancelLinks() {
        document.querySelectorAll('.cancel-link').forEach(function (link) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                close();
            });
        });
    }

    Popup.modal = modal;
    Popup.close = close;
    Popup.reloadHost = reloadHost;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wireCancelLinks);
    } else {
        wireCancelLinks();
    }
})(window.UnfoldExtraFilerPopup);
