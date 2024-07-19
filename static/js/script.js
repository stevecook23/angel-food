$(document).ready(function () {
  $(".sidenav").sidenav({edge: "right"});
  $(".collapsible").collapsible();
  $(".tooltipped").tooltip();
  $("select").formSelect();
  $(".datepicker").datepicker({
      format: "dd mmmm, yyyy",
      yearRange: 3,
      showClearBtn: true,
      i18n: {
          done: "Select"
      }
  });
});


document.addEventListener('DOMContentLoaded', function() {
  M.AutoInit();
  M.updateTextFields();
});


document.addEventListener('DOMContentLoaded', function() {
  // Initialize all modals
  var elems = document.querySelectorAll('.modal');
  var instances = M.Modal.init(elems);

  var deleteButtons = document.querySelectorAll('.delete-place, .delete-cuisine');
  var confirmDelete = document.getElementById('confirmDelete');
  var deleteUrl;

  // Attach event listeners to all delete buttons
  deleteButtons.forEach(function(button) {
      button.addEventListener('click', function(e) {
          e.preventDefault();
          deleteUrl = this.getAttribute('href');
          var instance = M.Modal.getInstance(document.getElementById('deleteModal'));
          instance.open();
      });
  });

  // Confirm delete action
  confirmDelete.addEventListener('click', function() {
      if (deleteUrl) {
          window.location.href = deleteUrl;
      }
  });
});

/*
    vanilla JavaScript for MaterializeCSS initialization
*/

// document.addEventListener('DOMContentLoaded', function () {
//     let sidenavs = document.querySelectorAll(".sidenav");
//     let sidenavsInstance = M.Sidenav.init(sidenavs, {edge: "right"});
//     let collapsibles = document.querySelectorAll(".collapsible");
//     let collapsiblesInstance = M.Collapsible.init(collapsibles);
//     let tooltips = document.querySelectorAll(".tooltipped");
//     let tooltipsInstance = M.Tooltip.init(tooltips);
//     let selects = document.querySelectorAll("select");
//     let selectsInstance = M.FormSelect.init(selects);
//     let datepickers = document.querySelectorAll(".datepicker");
//     let datepickersInstance = M.Datepicker.init(datepickers, {
//         format: "dd mmmm, yyyy",
//         yearRange: 3,
//         showClearBtn: true,
//         i18n: {
//             done: "Select"
//         }
//     });
// });