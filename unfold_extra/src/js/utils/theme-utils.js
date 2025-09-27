export const KEY_UNFOLD = 'adminTheme'; // JSON-encoded: "light" | "dark" | "auto"
export const KEY_CMS = 'theme';

export function applyTheme(theme) {
    if (!theme) return;
    console.log('applyTheme', theme);
    let normalizedTheme = theme;
    if (normalizedTheme && normalizedTheme[0] === '"') {
        try {
            normalizedTheme = JSON.parse(normalizedTheme);
        } catch {
        }
    }
    if (!['light', 'dark', 'auto'].includes(normalizedTheme)) return;

    const html = document.documentElement;
    html.setAttribute('data-theme', normalizedTheme);
    html.classList.remove('dark');

    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = (normalizedTheme === 'dark') || (normalizedTheme === 'auto' && prefersDark);
    if (isDark) html.classList.add('dark');
}

export function readTheme() {
    try {
        const theme_unfold = localStorage.getItem(KEY_UNFOLD);
        if (theme_unfold != null) return JSON.parse(theme_unfold);
    } catch {
    }
    // }
    // try {
    //     const theme_cms = localStorage.getItem(KEY_CMS);
    //     if (theme_cms != null) return JSON.parse(theme_cms);
    // } catch {
    // }
    return null;
}