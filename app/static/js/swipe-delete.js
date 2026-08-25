document.addEventListener("DOMContentLoaded", function () {
  var REVEAL_WIDTH = 64;
  var THRESHOLD = 28;

  document.querySelectorAll("[data-swipeable]").forEach(function (row) {
    var startX = null;
    var currentX = 0;
    var dragging = false;

    function reset() {
      row.style.transition = "transform 0.2s ease";
      row.style.transform = "translateX(0)";
      currentX = 0;
    }

    row.addEventListener("touchstart", function (e) {
      startX = e.touches[0].clientX;
      dragging = true;
      row.style.transition = "none";
    });

    row.addEventListener("touchmove", function (e) {
      if (!dragging || startX === null) return;
      var deltaX = e.touches[0].clientX - startX;
      currentX = Math.max(-REVEAL_WIDTH, Math.min(0, deltaX));
      row.style.transform = "translateX(" + currentX + "px)";
    });

    row.addEventListener("touchend", function () {
      dragging = false;
      row.style.transition = "transform 0.2s ease";
      if (currentX < -THRESHOLD) {
        row.style.transform = "translateX(-" + REVEAL_WIDTH + "px)";
        currentX = -REVEAL_WIDTH;
      } else {
        reset();
      }
    });

    // Tapping elsewhere closes any open swipe row.
    document.addEventListener("touchstart", function (e) {
      if (row.contains(e.target)) return;
      if (currentX !== 0) reset();
    });
  });
});
