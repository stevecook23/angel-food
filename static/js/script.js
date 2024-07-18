$(document).ready(function () {
  $(".sidenav").sidenav({ edge: "right" });
});

// Ensure showAlert is defined only if not already defined
if (typeof window.showAlert === "undefined") {
  window.showAlert = function(title, message) {
    alert(title + ": " + message);
  };
}