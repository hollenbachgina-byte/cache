document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector("[data-filters-toggle]");
  var panel = document.querySelector("[data-filters-panel]");
  if (!toggle || !panel) return;

  toggle.addEventListener("click", function () {
    panel.classList.toggle("open");
  });

  document.addEventListener("click", function (event) {
    if (!panel.contains(event.target) && !toggle.contains(event.target)) {
      panel.classList.remove("open");
    }
  });
});
