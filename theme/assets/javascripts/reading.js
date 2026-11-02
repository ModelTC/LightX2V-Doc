/* Native details/anchors work without JS; close the mobile outline on selection. */
(() => {
  "use strict";
  const outline = document.querySelector(".lx-mobile-toc");
  if (!outline) return;
  outline.addEventListener("click", event => {
    const link = event.target.closest("a[href^='#']");
    if (!link) return;
    const heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (!heading) return;
    outline.open = false;
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
  });
})();
