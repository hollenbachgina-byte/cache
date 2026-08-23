document.addEventListener("DOMContentLoaded", function () {
  var el = document.querySelector("[data-count-up]");
  if (!el) return;

  var container = document.querySelector("[data-previous-total]");
  var start = parseFloat(container.dataset.previousTotal);
  var end = parseFloat(container.dataset.newTotal);
  var deltaEl = document.querySelector("[data-success-delta]");
  var duration = 1300;
  var startTime = null;

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function formatCurrency(value) {
    return "$" + Math.round(value).toLocaleString("en-US");
  }

  function step(timestamp) {
    if (startTime === null) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var current = start + (end - start) * easeOutCubic(progress);
    el.textContent = formatCurrency(current);

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      el.textContent = formatCurrency(end);
      if (deltaEl) deltaEl.style.visibility = "visible";
    }
  }

  requestAnimationFrame(step);
});
