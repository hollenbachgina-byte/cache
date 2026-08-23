document.addEventListener("DOMContentLoaded", function () {
  var MAX_DIMENSION = 1200;
  var JPEG_QUALITY = 0.7;

  var input = document.querySelector("[data-photo-input]");
  var preview = document.querySelector("[data-photo-preview]");
  var placeholderIcon = document.querySelector("[data-photo-placeholder-icon]");
  var placeholderText = document.querySelector("[data-photo-placeholder-text]");
  if (!input) return;

  input.addEventListener("change", function () {
    var file = input.files && input.files[0];
    if (!file) return;

    var reader = new FileReader();
    reader.onload = function (event) {
      var img = new Image();
      img.onload = function () {
        var scale = Math.min(1, MAX_DIMENSION / Math.max(img.width, img.height));
        var canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);

        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(
          function (blob) {
            if (!blob) return;

            try {
              var compressedFile = new File([blob], "photo.jpg", { type: "image/jpeg" });
              var dataTransfer = new DataTransfer();
              dataTransfer.items.add(compressedFile);
              input.files = dataTransfer.files;
            } catch (err) {
              // DataTransfer/File construction unsupported — fall back to the
              // original file; server-side Pillow validation is the safety net.
            }

            if (preview) {
              preview.src = URL.createObjectURL(blob);
              preview.style.display = "block";
            }
            if (placeholderIcon) placeholderIcon.style.display = "none";
            if (placeholderText) placeholderText.style.display = "none";

            // Avatar upload (Profile screen) has no separate fields to fill
            // in first, so it submits itself the moment compression is done
            // rather than waiting for an explicit "Save" tap.
            var ownForm = input.closest("form");
            if (ownForm && ownForm.hasAttribute("data-photo-auto-submit")) {
              var autoOverlay = document.querySelector("[data-uploading-overlay]");
              if (autoOverlay) autoOverlay.style.display = "flex";
              ownForm.submit();
            }
          },
          "image/jpeg",
          JPEG_QUALITY
        );
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  });

  var form = document.querySelector("[data-photo-form]");
  var submitBtn = document.querySelector("[data-submit-btn]");
  var overlay = document.querySelector("[data-uploading-overlay]");

  if (form && submitBtn) {
    form.addEventListener("submit", function () {
      submitBtn.disabled = true;
      if (overlay) overlay.style.display = "flex";
    });
  }
});
