/* Pinned MathJax v3.2.2 via zensical.toml. Number every displayed equation.
   Every source .md scientific relation is typeset via pymdownx.arithmatex.
   This is configuration, NOT a scientific notation/algorithm change. */
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "all",
    tagSide: "right",
    useLabelIds: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};
// Zensical's documented instant-navigation event lifecycle (MathJax 3).
document$.subscribe(() => {
  if (!window.MathJax || !MathJax.typesetPromise) return;
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
