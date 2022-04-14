var mode = "foreign_first";
var show_diacritic = false;
var click_state = 0;
var word_index = 0;
var word;
var previous_words = [];

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

  function setup_buttons() {
    $("#set-words-count").val(words.length);
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const language = urlParams.get("language");
    var base_url = window.location.origin + "/articles/config";
    var seen_cutoff = Math.max(word.index + 1, 500);

    $("#examples-button").attr(
      "href",
      base_url +
        "?language=" +
        language +
        "&known_cutoff=" +
        (word.index - 1) +
        "&practice_cutoff=" +
        word.index +
        "&seen_cutoff=" +
        seen_cutoff
    );

    $("#save_button_" + 0).css("background-color", "#bad3da");
    $("#save_button_" + 1).css("background-color", "#bad3da");
    $("#save_button_" + 2).css("background-color", "#bad3da");
    $("#save_button_" + 3).css("background-color", "#bad3da");

    definition_url =
      "https://en.wiktionary.org/wiki/" + word["word"] + "#Arabic";
    $("#definition-button").attr("href", definition_url);
  }

  function toggle_diacritic() {
    show_diacritic = !show_diacritic;
    foreign_word = show_diacritic ? word["word_diacritic"] : word["word"];

    if (mode == "foreign_first") {
      $("#top-word").text(foreign_word);
      $("#bottom-word").text(word["translation"]);
    } else {
      $("#top-word").text(word["translation"]);
      $("#bottom-word").text(foreign_word);
    }
  }

  function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function save_word() {
    add_word_to_array(word);
    $("#save-button").hide();
  }

  function remove_word() {
    words.splice(word_index, 1);
    word = null;
    click_state = 0;
    word_index = word_index - 1;
    show_next_word();
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
      speak(word["word_diacritic"], speech_voice);
      root = word["root"];
      if (root == "") {
        root = "- - -";
      }
      $("#word-root").text(root);
    } else {
      show_next_word();
      $("#word-root").text("- - -");
      $("#next-button").text("^^^");
      $("#next-button").removeClass("next-button-next");
      $("#next-button").addClass("next-button-translate");

      click_state = 0;
    }
  }

  function change_mode() {
    if (mode == "translation_first") {
      mode = "foreign_first";
    } else {
      mode = "translation_first";
    }

    top_word_text = $("#top-word").text();
    bottom_word_text = $("#bottom-word").text();
    console.log(top_word_text);
    $("#top-word").text(bottom_word_text);
    $("#bottom-word").text(top_word_text);
  }

  function show_previous_word() {
    if (previous_words.length === 0) {
      return true;
    }

    prev_word = previous_words.pop();
    words.splice(word_index, 0, prev_word);
    word = words[word_index];

    click_state = 0;

    foreign_word = show_diacritic ? word["word_diacritic"] : word["word"];

    if (mode == "foreign_first") {
      $("#top-word").text(foreign_word);
      $("#bottom-word").text(word["translation"]);
    } else {
      $("#top-word").text(word["translation"]);
      $("#bottom-word").text(foreign_word);
    }

    $("#word-root").text("- - -");

    setup_buttons();

    $("#bottom-word").hide();
    $("#bottom-word-holder").show();
    $("#back-button").hide();
  }

  function show_next_word() {
    if (word) {
      previous_words.push(word);
    }

    word_index = word_index + 1;
    if (word_index >= words.length) {
      shuffleArray(words);
      word_index = 0;
    }

    word = words[word_index];
    foreign_word = show_diacritic ? word["word_diacritic"] : word["word"];

    if (mode == "foreign_first") {
      $("#top-word").text(foreign_word);
      $("#bottom-word").text(word["translation"]);
    } else {
      $("#top-word").text(word["translation"]);
      $("#bottom-word").text(foreign_word);
    }

    $("#bottom-word").hide();
    $("#bottom-word-holder").show();

    setup_buttons();

    if (previous_words.length > 0) {
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
    change_mode();
  });

  $(function () {
    $(window).keydown(function (e) {
      var key = e.which;
      console.log(key);
      if (key == "32" || key == "13" || key == "39") {
        clicked_next_word();
      } else if (key == "37") {
        show_previous_word();
      } else if (key == "83" || key == "38") {
        save_word();
      } else if (key == "68") {
        toggle_diacritic();
      } else if (key == "82" || key == "16") {
        speak(word["word_diacritic"], speech_voice);
      } else if (key == "8") {
        remove_word();
        //   } else if (key == "49") {
        //     clicked_update(0);
        //   } else if (key == "50") {
        //     clicked_update(1);
        //   } else if (key == "51") {
        //     clicked_update(2);
        // } else if (key == "51") {
        //   clicked_update(2);
      }
    });
  });
});

async function clicked_update(rating) {
  const db = await idb.openDB("testDB", 1, {
    upgrade(db) {
      const store = db.createObjectStore("bllooop", {
        keyPath: "word",
      });
    },
  });

  $("#save_button_" + 0).css("background-color", "#bad3da");
  $("#save_button_" + 1).css("background-color", "#bad3da");
  $("#save_button_" + 2).css("background-color", "#bad3da");
  $("#save_button_" + 3).css("background-color", "#bad3da");

  $("#save_button_" + rating).css("background-color", "red");
  await db.put("bllooop", { rating: rating, word: word.word });
}

async function filter_words_by_rating(rating) {
  const db = await idb.openDB("testDB", 1, {
    upgrade(db) {
      const store = db.createObjectStore("bllooop", {
        keyPath: "word",
      });
    },
  });

  words.forEach(async (w) => {
    w = w["word"];
    res = await db.get("bllooop", w);
    if (res) {
      if (res["rating"] == rating) {
        removeWordFromWords(w);
      }
    }
  });
}

function removeWordFromWords(w) {
  words = words.filter(function (value) {
    return value["word"] !== w;
  });
}

function update_root() {
  console.log("update_root");

  let new_root = document.getElementById("new_root").value;
  w = word.word;

  data = {
    new_user_root: new_root,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + w + "/",
    data: JSON.stringify(data),
    processData: false,
    contentType: "application/json",
  })
    .done(function () {
      alert("success");
    })
    .fail(function () {
      alert("error");
    })
    .always(function () {
      // alert("complete");
    });
}


function set_words_count(){
  let words_count = document.getElementById("set-words-count").value;
  words = words.slice(0, words_count);
}