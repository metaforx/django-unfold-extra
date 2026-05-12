(function () {
  "use strict";

  var cmsSiteReloadPending = false;

  function deriveWidgetName(widget) {
    // Django admin rewrites `__prefix__` in id/name attributes but leaves the
    // JSON inside `<script type="application/json">` untouched. Read the real
    // name back from the first sibling <select> so PageSelectWidget can find
    // the dynamically inserted inline row's elements.
    var container = widget.previousElementSibling;
    if (!container) {
      return null;
    }
    var siteSelect = container.querySelector("select[id$='_0']");
    if (!siteSelect || !siteSelect.id) {
      return null;
    }
    return siteSelect.id.replace(/^id_/, "").replace(/_0$/, "");
  }

  function initPageSelectWidgets(root) {
    if (!window.CMS || !window.CMS.PageSelectWidget || !root) {
      return;
    }

    var widgets = root.querySelectorAll("[data-cms-widget-pageselect]");
    widgets.forEach(function (widget) {
      if (widget.dataset.cmsPageselectInlineInit === "1") {
        return;
      }

      var script = widget.querySelector("script");
      if (!script) {
        return;
      }

      try {
        var config = JSON.parse(script.textContent || "{}");
        var actualName = deriveWidgetName(widget);
        if (actualName) {
          config.name = actualName;
        }
        new window.CMS.PageSelectWidget(config);
        widget.dataset.cmsPageselectInlineInit = "1";
      } catch (error) {
        // Keep admin usable even if one inline payload is malformed.
      }
    });
  }

  document.addEventListener("formset:added", function (event) {
    if (event.target instanceof Element) {
      initPageSelectWidgets(event.target);
    }
  });

  function requestReloadAfterSiteSwitch() {
    if (cmsSiteReloadPending) {
      return;
    }

    cmsSiteReloadPending = true;
    // Wait until CMS has persisted the selected admin site in session.
    window.setTimeout(function () {
      window.location.reload();
    }, 150);
  }

  function isCmsSiteSwitchHref(href) {
    if (!href) {
      return false;
    }

    return (
      href.indexOf("cms_admin_site") !== -1 ||
      (href.indexOf("/admin/cms/") !== -1 && href.indexOf("site") !== -1)
    );
  }

  document.addEventListener("click", function (event) {
    var link = event.target && event.target.closest ? event.target.closest("a") : null;
    if (!link) {
      return;
    }

    if (isCmsSiteSwitchHref(link.getAttribute("href") || "")) {
      requestReloadAfterSiteSwitch();
    }
  });

  document.addEventListener("change", function (event) {
    var target = event.target;
    if (!(target instanceof HTMLSelectElement)) {
      return;
    }

    var id = target.id || "";
    var name = target.name || "";
    if (id.indexOf("site") !== -1 || name.indexOf("site") !== -1) {
      requestReloadAfterSiteSwitch();
    }
  });
})();
