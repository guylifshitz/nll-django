$(document).ready(function () {
  function show_full_translation(event) {
    $(event.target)
      .parent()
      .parent()
      .parent()
      .find(".title_translation")
      .toggle();
    position_tooltips();
  }
  $(".button_full_translation").on("click", show_full_translation);

  function show_partial_translation(event) {
    $(event.target).parent().parent().parent().find(".title_mix").toggle();
    position_tooltips();
  }
  $(".button_partial_translation").on("click", show_partial_translation);

  function position_tooltips() {
    var tooltips = $(".word_tooltip");
    $.each(tooltips, function (index, tooltip) {
      var box = tooltip.previousElementSibling.getBoundingClientRect();
      tooltip.style.position = "absolute";
      tooltip.style.top = box.top + 20 + window.scrollY + "px";
      tooltip.style.left = box.left + (box.right - box.left) / 2 - 50 + "px";
    });
  }
  position_tooltips();
  window.addEventListener("resize", position_tooltips, true);
});
