import {KEY_CMS, KEY_UNFOLD, applyTheme} from './utils/theme-utils.js';

// --- CMS sideframe reload after language switch ---
// cms_set_language appends ?reload_window to the redirect (same pattern
// CMS uses in admin/cms/usersettings/change_form.html).  When the target
// page loads inside a CMS sideframe we save the clean URL and reload the
// parent so the toolbar and frontend page pick up the new language.
if (location.href.indexOf('reload_window') > -1) {
    window.addEventListener('load', function () {
        // setTimeout mirrors CMS's own timing: the sideframe load event
        // fires after window.onload, so we yield once.
        setTimeout(function () {
            try {
                var CMS = window.parent.CMS;
                if (CMS && CMS.API) {
                    CMS.settings.sideframe = CMS.settings.sideframe || {};
                    CMS.settings.sideframe.url = location.href.replace(/[?&]reload_window/, '');
                    CMS.settings = CMS.API.Helpers.setSettings(CMS.settings);
                    CMS.API.Helpers.reloadBrowser();
                    return;
                }
            } catch (e) {}
            // Not in a sideframe — just clean up the URL.
            history.replaceState(null, '', location.href.replace(/[?&]reload_window/, ''));
        }, 0);
    });
}

// --- Theme sync ---
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