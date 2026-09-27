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
    const root = document.documentElement;
    window.Alpine.effect(function () {
        const theme = window.Alpine.$data(root).adminTheme;
        if (!valid(theme) || theme === root.getAttribute('data-theme')) return;
        syncTheme(KEY_UNFOLD, theme);
    });
});
