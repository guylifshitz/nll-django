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

  function speak(text) {
    var msg = new SpeechSynthesisUtterance();
    msg.text = text;
    msg.lang = speech_voice;
    msg.rate = 0.8;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
  }

  function speak_title(event) {
    title_text = $(event.target).parent().parent().parent().find(".title"). attr("text");
    speak(title_text);
  }

  function show_partial_translation(event) {
    $(event.target).parent().parent().parent().find(".title_mix").toggle();
    position_tooltips();
  }

  $(".button_partial_translation").on("click", show_partial_translation);
  $(".button_full_translation").on("click", show_full_translation);

  $(".button_speak").on("click", speak_title);

  $(".word").on("click", function (element) {
    tooltip2 =
      element.target.nextElementSibling.getElementsByClassName(
        "mix_tooltip_2"
      )[0];
    $(tooltip2).toggle();
  });

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
