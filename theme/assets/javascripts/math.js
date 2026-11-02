/* Render only Arithmatex nodes; KaTeX and its fonts are served locally. */
document$.subscribe(() => {
  document.querySelectorAll(".arithmatex").forEach((element) => {
    if (element.dataset.rendered) return;
    const source = element.textContent.trim();
    const displayMode = source.startsWith("\\[");
    katex.render(source.slice(2, -2), element, {
      displayMode,
      throwOnError: false,
      trust: false,
    });
    element.dataset.rendered = "true";
  });
});
