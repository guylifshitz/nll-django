var mode = "foreign_first";
var click_state = 0;
var word_index = 0;
var word;
var previous_word;

$(document).ready(function () {
  function speak(text, language) {
    var msg = new SpeechSynthesisUtterance();
    msg.text = text;
    msg.lang = language;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
  }
  const shuffleArray = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const temp = array[i];
      array[i] = array[j];
      array[j] = temp;
    }
  };

  function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
  function save_word() {
    add_word_to_array(word);
    $("#save-button").hide();
  }

  function add_word_to_array(word) {
    slice_index = getRandomInt(word_index, words.length);
    words.splice(slice_index, 0, word);
  }

  function clicked_next_word() {
    if (click_state == 0) {
      $("#bottom-word").show();
      $("#bottom-word-holder").hide();
      $("#next-button").text(">>>");
      $("#next-button").addClass("next-button-next");
      $("#next-button").removeClass("next-button-translate");
      click_state = 1;
      speak(word["word"], "ar-SA");
    } else {
      show_next_word();
      $("#next-button").text("^^^");
      $("#next-button").removeClass("next-button-next");
      $("#next-button").addClass("next-button-translate");

      click_state = 0;
    }
  }

  function change_mode(new_mode) {
    mode = new_mode;
    top_word_text = $("#top-word").text;
    bottom_word_text = $("#bottom-word").text;
    $("#top-word").text(bottom_word_text);
    $("#bottom-word").text(top_word_text);
  }

  function show_previous_word() {
    word_index = word_index - 1;
    word = previous_word;
    var click_state = 0;

    $("#top-word").text(word["word"]);
    $("#bottom-word").text(word["translation"]);

    definition_url =
      "https://en.wiktionary.org/wiki/" + word["word"] + "#Arabic";
    $("#definition-button").attr("href", definition_url);

    $("#bottom-word").hide();
    $("#bottom-word-holder").show();
    $("#back-button").hide();
  }

  function show_next_word() {
    previous_word = word;

    word_index = word_index + 1;

    if (word_index >= words.length) {
      shuffleArray(words);
      word_index = 0;
    }

    word = words[word_index];
    if (mode == "foreign_first") {
      $("#top-word").text(word["word"]);
      $("#bottom-word").text(word["translation"]);
    } else {
      $("#top-word").text(word["translation"]);
      $("#bottom-word").text(word["word"]);
    }

    $("#bottom-word").hide();
    $("#bottom-word-holder").show();

    definition_url =
      "https://en.wiktionary.org/wiki/" + word["word"] + "#Arabic";
    $("#definition-button").attr("href", definition_url);

    if (previous_word) {
      $("#back-button").show();
    }
    $("#save-button").show();
  }

  shuffleArray(words);
  show_next_word();

  $("#back-button").hide();

  $("#next-button").on("click", clicked_next_word);
  $("#save-button").on("click", function () {
    save_word();
  });
  $("#back-button").on("click", function () {
    show_previous_word();
  });
  $("#top-word").on("click", function () {
    if (mode == "translation_first") {
      mode = "foreign_first";
      $("#top-word").text(word["word"]);
      $("#bottom-word").text(word["translation"]);
    } else {
      mode = "translation_first";
      $("#top-word").text(word["translation"]);
      $("#bottom-word").text(word["word"]);
    }
  });

  $(function () {
    $(window).keydown(function (e) {
      var key = e.which;
      console.log(key);
      if (key == "32" || key == "13" || key == "39") {
        clicked_next_word();
      } else if (key == "37") {
        show_previous_word();
      } else if (key == "83") {
        save_word();
      } else if (key == "82") {
        speak(word["word"], "ar-SA");
      }
    });
  });
});

function update_root() {
  console.log("update_root");
  data = {
    new_user_root: "test",
  };

  $.post(
    "http://localhost:8001/apii/words/%D7%A9%D7%9C/",
    function (data, status) {
      console.log(res);
      console.log(status);
    }
  );
}
