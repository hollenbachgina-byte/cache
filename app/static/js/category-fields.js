document.addEventListener("DOMContentLoaded", function () {
  var CATEGORY_FIELDS = {
    "Clothing": ["size", "material", "color"],
    "Shoes": ["size", "material", "color"],
    "Bags": ["material", "dimensions", "color"],
    "Accessories": ["size", "dimensions", "material", "color"],
    "Electronics": ["storage_capacity"],
    "Home": ["dimensions", "material"]
  };

  var categoryInput = document.querySelector("[data-category-input]");
  var header = document.querySelector("[data-dynamic-fields-header]");
  var categoryLabel = document.querySelector("[data-dynamic-fields-category-label]");
  var fieldWraps = document.querySelectorAll("[data-field-wrap]");
  if (!categoryInput) return;

  function update() {
    var category = categoryInput.value.trim();
    var fields = CATEGORY_FIELDS[category] || [];

    fieldWraps.forEach(function (wrap) {
      var fieldName = wrap.getAttribute("data-field-wrap");
      wrap.classList.toggle("visible", fields.indexOf(fieldName) !== -1);
    });

    if (fields.length) {
      if (header) header.style.display = "block";
      if (categoryLabel) categoryLabel.textContent = category;
    } else {
      if (header) header.style.display = "none";
    }
  }

  categoryInput.addEventListener("input", update);
  categoryInput.addEventListener("change", update);
  update();
});
