import {KEY_CMS, KEY_UNFOLD, applyTheme} from './utils/theme-utils.js';

let mirroring = false;

applyTheme(localStorage.getItem(KEY_UNFOLD))

const normalize = (val) => {
    if (val == null) return null;
    if (val[0] === '"') {
        try {
            return JSON.parse(val);
        } catch {
        }
    }
    return val;
};

const valid = (t) => t === 'light' || t === 'dark' || t === 'auto';

/** Unfold's Alpine theme state on this page, or null outside Unfold. */
function unfoldState() {
    if (!window.Alpine) return null;
    const state = window.Alpine.$data(document.documentElement);
    return state.adminTheme === undefined ? null : state;
}

/** Mirror a theme change from `sourceKey` to the other store, then apply it to this document. */
function syncTheme(sourceKey, theme) {
    try {
        mirroring = true;

        if (sourceKey === KEY_UNFOLD) {
            // mirror to CMS as plain string if different
            const current = localStorage.getItem(KEY_CMS);
            if (current !== theme) localStorage.setItem(KEY_CMS, theme);
        } else {
            // mirror to UNFOLD as JSON string if different
            const current = localStorage.getItem(KEY_UNFOLD);
            const target = JSON.stringify(theme);
            if (current !== target) localStorage.setItem(KEY_UNFOLD, target);
        }
    } finally {
        mirroring = false;
    }

    // keep Unfold's switcher in step, it never re-reads localStorage
    const state = unfoldState();
    if (state && state.adminTheme !== theme) state.adminTheme = theme;

    applyTheme(theme);
}

window.addEventListener('storage', (e) => {
    if (e.key !== KEY_UNFOLD && e.key !== KEY_CMS) return;
    if (mirroring) return; // ignore events caused by our own mirror write

    const raw = typeof e.newValue === 'string' ? e.newValue : null;
    const theme = normalize(raw);
    if (!valid(theme)) return;

    syncTheme(e.key, theme);
});

// Unfold's switcher changes adminTheme in this window, which fires no 'storage' event here.
document.addEventListener('alpine:initialized', function () {
    const state = unfoldState();
    if (!state) return;
    window.Alpine.effect(function () {
        const theme = state.adminTheme;
        if (!valid(theme) || theme === document.documentElement.getAttribute('data-theme')) return;
        syncTheme(KEY_UNFOLD, theme);
    });
});

// The CMS toolbar sets data-theme in this window and on its sideframe, which fires no 'storage' event here.
new MutationObserver(function () {
    const theme = document.documentElement.getAttribute('data-theme');
    if (!valid(theme) || theme === normalize(localStorage.getItem(KEY_UNFOLD))) return;
    syncTheme(KEY_CMS, theme);
}).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
