/**
 * Unfold Extra - filer admin actions
 *
 * Restores the admin selection wiring that Unfold's admin/js/actions.js override
 * drops on filer's directory listing: row highlighting, the selection counter and
 * the select-all toggles, for both the table and thumbnail list types.
 */
'use strict';

/* global interpolate, ngettext */

(function () {
    // Select-all toggles: one in table view, three (scoped by value) in grid.
    const TOGGLES = {
        'action-toggle': null,
        'all-items-action-toggle': null,
        'folders-action-toggle': 'folder-',
        'files-action-toggle': 'file-'
    };

    function init() {
        const form = document.getElementById('changelist-form');

        if (!form || !document.getElementById('result_list')) return;

        function boxes() {
            return Array.from(form.querySelectorAll('input.action-select'));
        }

        // filer marks .list-item itself, but only on real clicks, never rows.
        function markRow(box) {
            const row = box.closest('tr, .list-item');

            if (row) row.classList.toggle('selected', box.checked);
        }

        // filer's toolbar buttons are inert without this class.
        function syncToolbar(selected) {
            const wrapper = document.querySelector('.actions-wrapper');

            if (wrapper) wrapper.classList.toggle('action-selected', selected > 0);
        }

        /**
         * Django's counter wording, falling back when jsi18n is unavailable.
         */
        function formatCounter(selected, total) {
            if (typeof interpolate !== 'function' || typeof ngettext !== 'function') {
                return selected + ' of ' + total + ' selected';
            }

            return interpolate(
                ngettext('%(sel)s of %(cnt)s selected', '%(sel)s of %(cnt)s selected', selected),
                { sel: selected, cnt: total },
                true
            );
        }

        function update() {
            const all = boxes();
            const selected = all.filter(function (box) { return box.checked; }).length;

            document.querySelectorAll('span.action-counter').forEach(function (counter) {
                const total = Number(counter.dataset.actionsIcnt) || all.length;
                counter.textContent = formatCounter(selected, total);
            });

            const master = document.getElementById('action-toggle');

            if (master) master.checked = all.length > 0 && selected === all.length;

            syncToolbar(selected);
        }

        form.addEventListener('change', function (event) {
            if (!event.target.classList.contains('action-select')) return;

            markRow(event.target);
            update();
        });

        Object.keys(TOGGLES).forEach(function (id) {
            const toggle = document.getElementById(id);
            const prefix = TOGGLES[id];

            if (!toggle) return;

            toggle.addEventListener('change', function () {
                boxes().forEach(function (box) {
                    if (prefix && box.value.indexOf(prefix) !== 0) return;

                    box.checked = toggle.checked;
                    markRow(box);
                });

                update();
            });
        });

        update();
    }

    if (document.readyState !== 'loading') {
        init();
    } else {
        document.addEventListener('DOMContentLoaded', init);
    }
})();
