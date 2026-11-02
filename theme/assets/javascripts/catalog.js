/* Progressive enhancement: the complete model list remains readable without JS. */
(() => {
  "use strict";
  const catalog = document.querySelector("[data-model-catalog]");
  if (!catalog) return;

  const input = catalog.querySelector("input[type='search']");
  const buttons = [...catalog.querySelectorAll("[data-filter]")];
  const models = [...catalog.querySelectorAll(".lx-model")];
  const count = catalog.querySelector(".lx-model-count");
  const empty = catalog.querySelector(".lx-model-empty");
  const clearActive = catalog.querySelector("[data-clear-active]");
  const clearCategory = catalog.querySelector("[data-clear-category]");
  const languageSwitch = document.querySelector(".lx-language-switch");
  const categories = new Set(buttons.map(button => button.dataset.filter));
  const normalize = value => value.normalize("NFKC").toLocaleLowerCase().trim();
  const searchable = new Map(models.map(model => [model, normalize(model.dataset.search)]));
  let category = "all";

  function syncURL() {
    const url = new URL(window.location.href);
    const term = input.value.trim();
    // Avoid Material's own search parameters. replaceState also lets browser
    // Back restore a filtered catalog without one history entry per keystroke.
    term ? url.searchParams.set("model", term) : url.searchParams.delete("model");
    category === "all" ? url.searchParams.delete("task") : url.searchParams.set("task", category);
    if (url.href !== window.location.href) window.history.replaceState(window.history.state, "", url);
    if (languageSwitch) {
      const alternate = new URL(languageSwitch.href);
      for (const key of ["model", "task"]) {
        url.searchParams.has(key) ? alternate.searchParams.set(key, url.searchParams.get(key)) : alternate.searchParams.delete(key);
      }
      languageSwitch.href = alternate.href;
    }
  }

  function filter() {
    const terms = normalize(input.value).split(/\s+/).filter(Boolean);
    const counts = new Map([...categories].map(key => [key, 0]));
    let visible = 0;
    for (const model of models) {
      const matchesQuery = terms.every(term => searchable.get(model).includes(term));
      if (matchesQuery) {
        counts.set("all", counts.get("all") + 1);
        counts.set(model.dataset.category, counts.get(model.dataset.category) + 1);
      }
      const matches = (category === "all" || model.dataset.category === category)
        && matchesQuery;
      model.hidden = !matches;
      if (matches) visible += 1;
    }
    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.filter === category));
      button.querySelector("[data-filter-count]").textContent = counts.get(button.dataset.filter);
    }
    count.textContent = catalog.dataset.countTemplate
      .replace("{visible}", visible).replace("{total}", models.length);
    empty.hidden = visible > 0;
    clearCategory.hidden = visible > 0 || counts.get("all") === 0;
    clearCategory.textContent = catalog.dataset.otherTemplate.replace("{count}", counts.get("all"));
    clearActive.hidden = category === "all" && terms.length === 0;
    syncURL();
  }

  function restore() {
    const params = new URL(window.location.href).searchParams;
    input.value = params.get("model") || "";
    const task = params.get("task");
    category = categories.has(task) ? task : "all";
    filter();
  }

  buttons.forEach(button => button.addEventListener("click", () => {
    category = button.dataset.filter;
    filter();
  }));
  input.addEventListener("input", filter);
  clearCategory.addEventListener("click", () => {
    category = "all";
    filter();
    input.focus({ preventScroll: true });
  });
  catalog.querySelectorAll("[data-reset-filters]").forEach(button => button.addEventListener("click", () => {
    category = "all";
    input.value = "";
    filter();
    input.focus({ preventScroll: true });
  }));
  window.addEventListener("pageshow", restore);
  window.addEventListener("popstate", restore);
  catalog.dataset.enhanced = "true";
  restore();
})();
