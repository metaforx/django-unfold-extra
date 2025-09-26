(function () {
  // only when admin runs inside an iframe
  if (window.top === window) return;
  function postTheme() {
    var html = document.documentElement;
    var isDark = html.classList.contains('dark') ||
                 html.getAttribute('data-theme') === 'dark';
    try {
      window.parent.postMessage(
        { type: 'unfold-theme', theme: isDark ? 'dark' : 'light' },
        window.location.origin
      );
    } catch (e) {}
  }
  postTheme();
  new MutationObserver(postTheme).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class","data-theme"],
  });
})();