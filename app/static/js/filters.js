document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector("[data-filters-toggle]");
  var panel = document.querySelector("[data-filters-panel]");
  if (toggle && panel) {
    toggle.addEventListener("click", function () {
      panel.classList.toggle("open");
    });

    document.addEventListener("click", function (event) {
      if (!panel.contains(event.target) && !toggle.contains(event.target)) {
        panel.classList.remove("open");
      }
    });
  }

  // My Cache search — narrows whatever the server already rendered (i.e.
  // on top of any active category/archived filters), doesn't replace them.
  var searchInput = document.querySelector("[data-item-search]");
  var itemGrid = document.querySelector("[data-item-grid]");
  if (searchInput && itemGrid) {
    var itemRows = itemGrid.querySelectorAll("[data-item-row]");
    var noMatches = document.querySelector("[data-no-search-matches]");

    searchInput.addEventListener("input", function () {
      var query = searchInput.value.trim().toLowerCase();
      var visibleCount = 0;

      itemRows.forEach(function (row) {
        var visible = !query || row.dataset.name.indexOf(query) !== -1;
        row.style.display = visible ? "block" : "none";
        if (visible) visibleCount++;
      });

      itemGrid.style.display = visibleCount === 0 ? "none" : "grid";
      if (noMatches) noMatches.style.display = visibleCount === 0 ? "block" : "none";
    });
  }
});
