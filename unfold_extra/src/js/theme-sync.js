import {KEY_CMS, KEY_UNFOLD, applyTheme} from './utils/theme-utils.js';

let mirroring = false;

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

window.addEventListener('storage', (e) => {
    if (e.key !== KEY_UNFOLD && e.key !== KEY_CMS) return;
    if (mirroring) return; // ignore events caused by our own mirror write

    const raw = typeof e.newValue === 'string' ? e.newValue : null;
    const theme = normalize(raw);
    if (!valid(theme)) return;

    try {
        mirroring = true;

        if (e.key === KEY_UNFOLD) {
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
});