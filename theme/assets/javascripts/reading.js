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

/* Appearance menu: Material owns persistence and OS preference changes. */
(() => {
  "use strict";
  const root = document.querySelector(".lx-theme");
  if (!root) return;
  const toggle = root.querySelector(".lx-theme-toggle");
  const menu = root.querySelector(".lx-theme-menu");
  const choices = [...menu.querySelectorAll(".lx-theme-choice")];
  const inputs = [...root.querySelectorAll('[data-md-component="palette"] input')];
  const selectedIndex = () => Math.max(0, inputs.findIndex(input => input.dataset.mdColorMedia === document.body.dataset.mdColorMedia));

  const sync = () => {
    const index = selectedIndex();
    choices.forEach((choice, i) => choice.setAttribute("aria-checked", String(i === index)));
    const label = `${toggle.dataset.label}: ${choices[index].querySelector(".lx-theme-label").textContent}`;
    toggle.setAttribute("aria-label", label);
    toggle.title = label;
  };
  const focusChoice = index => {
    choices.forEach((choice, i) => { choice.tabIndex = i === index ? 0 : -1; });
    choices[index].focus();
  };
  const close = (restoreFocus = false) => {
    menu.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    if (restoreFocus) toggle.focus();
  };
  const open = (index = selectedIndex()) => {
    menu.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    focusChoice(index);
  };
  toggle.addEventListener("click", () => menu.hidden ? open() : close());
  toggle.addEventListener("keydown", event => {
    if (!["ArrowDown", "ArrowUp"].includes(event.key)) return;
    event.preventDefault();
    event.stopPropagation();
    open(event.key === "ArrowDown" ? 0 : choices.length - 1);
  });
  choices.forEach((choice, index) => choice.addEventListener("click", () => {
    inputs[index].click();
    sync();
    close(true);
  }));
  menu.addEventListener("keydown", event => {
    if (event.key === "Tab") {
      // Let the browser move focus before hiding the focused menu item.
      setTimeout(() => close(), 0);
      return;
    }
    const current = choices.indexOf(document.activeElement);
    let next;
    if (event.key === "ArrowDown") next = (current + 1) % choices.length;
    if (event.key === "ArrowUp") next = (current - 1 + choices.length) % choices.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = choices.length - 1;
    if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
      const match = choices.findIndex(choice => choice.querySelector(".lx-theme-label").textContent.toLowerCase().startsWith(event.key.toLowerCase()));
      if (match !== -1) next = match;
    }
    if (next === undefined) return;
    event.preventDefault();
    event.stopPropagation();
    focusChoice(next);
  });
  root.addEventListener("keydown", event => {
    if (event.key !== "Escape" || menu.hidden) return;
    event.preventDefault();
    event.stopPropagation();
    close(true);
  });
  document.addEventListener("pointerdown", event => {
    if (!root.contains(event.target)) close();
  });
  root.addEventListener("focusout", event => {
    if (!root.contains(event.relatedTarget)) close();
  });
  new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ["data-md-color-media"] });
  sync();
})();

/* Enhance Material's search presentation without replacing its search engine. */
(() => {
  "use strict";
  const toggle = document.getElementById("__search");
  const input = document.querySelector("[data-md-component='search-query']");
  const results = document.querySelector(".md-search-result__list");
  if (!toggle || !input || !results) return;

  const shortcut = document.querySelector(".lx-search-shortcut");
  if (shortcut && /Mac|iPad|iPhone/.test(navigator.userAgentData?.platform || navigator.platform)) {
    shortcut.textContent = "⌘ K";
  }
  document.addEventListener("keydown", event => {
    if (event.defaultPrevented || event.isComposing || event.repeat || event.altKey || event.shiftKey) return;
    if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== "k") return;
    event.preventDefault();
    if (!toggle.checked) toggle.click();
    requestAnimationFrame(() => { input.focus(); input.select(); });
  });
  document.querySelector(".lx-search-close")?.addEventListener("click", () => {
    if (toggle.checked) toggle.click();
  });

  // Both languages share page paths below the optional /en/ prefix.
  const pageKey = url => url.pathname.replace(/\/en\//, "/");
  const pages = new Map();
  document.querySelectorAll(".md-nav--primary a[href]").forEach(link => {
    const url = new URL(link.href);
    if (url.origin !== location.origin || url.hash) return;
    const section = link.closest("nav[data-md-level='1']")?.querySelector(":scope > .md-nav__title");
    pages.set(pageKey(url), {
      section: section?.textContent.trim() || "",
      title: link.textContent.trim()
    });
  });

  const enhanceResults = () => {
    results.querySelectorAll(".md-search-result__article:not([data-lx-search-ready])").forEach(article => {
      const link = article.closest("a[href]");
      const heading = article.querySelector("h2, h1");
      if (!link || !heading) return;
      const url = new URL(link.href);
      const page = pages.get(pageKey(url));
      const documentTitle = article.closest(".md-search-result__item")?.querySelector("h1")?.textContent.trim() || page?.title;
      const parts = [page?.section];
      if (article.querySelector("h2")) parts.push(documentTitle);
      const path = document.createElement("div");
      path.className = "lx-search-path";
      const trail = document.createElement("span");
      trail.textContent = parts.filter(Boolean).join(" › ");
      const language = document.createElement("span");
      language.className = "lx-search-language";
      language.textContent = /\/en\//.test(url.pathname) ? "EN" : "中文";
      path.append(trail, language);
      // Material may render table excerpts as bare text nodes as well as tags.
      const excerpt = document.createElement("div");
      excerpt.hidden = true;
      [...article.childNodes].forEach(node => {
        if (node.nodeType !== Node.ELEMENT_NODE || !node.matches("h1, h2, .md-search-result__icon")) {
          excerpt.append(node);
        }
      });
      article.append(excerpt, path);
      article.dataset.lxSearchReady = "";
    });
  };
  new MutationObserver(enhanceResults).observe(results, { childList: true, subtree: true });
  enhanceResults();
})();
