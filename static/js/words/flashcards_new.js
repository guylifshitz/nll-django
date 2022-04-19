// original_words
// all_words
// xxx_words
// prev_words
// next_words

// CONFIG VARS
const prev_words_to_keep = 10;

var all_words;
var XXXX_words;
var current_word;
var current_word_index = -1;
var largest_word_index = -1;

var top_word;
var bottom_word;
var root;
var word_state = 2;

function clicked_next_word() {
  if (word_state == 2) {
    get_next_word();
    set_word_top_bottom_root();
    word_state = 1;
    refresh_ui(word_state);
  } else {
    word_state = 2;
    refresh_ui(word_state);
    get_rating();
    speak_word();
  }
}

function clicked_previous_word() {
  current_word_index = Math.max(current_word_index - 1, 0);
  current_word = XXXX_words[current_word_index];

  set_word_top_bottom_root();
  word_state = 1;
  refresh_ui(word_state);
}

function set_word_top_bottom_root() {
  word = current_word["word"];
  if ($("#diacritic-toggle").hasClass("button-checked")) {
    word = current_word["word_diacritic"];
  }

  if ($("#swap-top-bottom").hasClass("button-checked")) {
    top_word = current_word["translation"];
    bottom_word = word;
  } else {
    top_word = word;
    bottom_word = current_word["translation"];
  }

  root = current_word["root"];
  if (root == "") {
    root = "---";
  }
}

function refresh_ui(ui_to_show) {
  if (ui_to_show == 1) {
    set_words_ui_one();
  } else {
    set_words_ui_two();
  }
}
function set_words_ui_one() {
  $("#word-top").text(top_word);
  $("#word-bottom").text("---");
  $("#word-root").text("---");

  fix_links();

  if (current_word_index == 0) {
    $("#button-previous").addClass("button-disabled");
  } else {
    $("#button-previous").removeClass("button-disabled");
  }

  clear_ratings();
}

function set_words_ui_two() {
  $("#word-top").text(top_word);
  $("#word-bottom").text(bottom_word);
  $("#word-root").text(root);
}

function get_next_word() {
  if (all_words.length == 0) {
    alert("Error 1617: Empty array not implemented");
  }

  current_word_index = current_word_index + 1;
  largest_word_index = Math.max(largest_word_index, current_word_index);

  if (current_word_index >= XXXX_words.length) {
    XXXX_words = XXXX_words.slice(-prev_words_to_keep);
    current_word_index = XXXX_words.length;
    largest_word_index = current_word_index;
    words_to_add = Array.from(all_words);
    shuffleArray(words_to_add);
    XXXX_words.push.apply(XXXX_words, words_to_add);
  }
  current_word = XXXX_words[current_word_index];
}

function toggle_checked(element) {
  if (element.classList.contains("button-checked")) {
    element.classList.remove("button-checked");
  } else {
    element.classList.add("button-checked");
  }
}

function fix_links() {
  $("#open-dictionary").attr(
    "href",
    "https://en.wiktionary.org/wiki/" + current_word["word"]
  );
  //TODO it would be nice if the articles config could take the word as a param, and know that that is the word we want to show
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const language = urlParams.get("language");
  var base_url = window.location.origin + "/articles/config";
  var seen_cutoff = Math.max(current_word["index"] + 1, 500);
  $("#open-examples").attr(
    "href",
    base_url +
      "?language=" +
      language +
      "&known_cutoff=" +
      (current_word["index"] - 1) +
      "&practice_cutoff=" +
      current_word["index"] +
      "&seen_cutoff=" +
      seen_cutoff
  );
}

function swap_top_bottom_words(element) {
  toggle_checked(element);
  set_word_top_bottom_root();
  refresh_ui(word_state);
}

function toggle_diacritic(element) {
  toggle_checked(element);
  set_word_top_bottom_root();
  refresh_ui(word_state);
}
function speak_word() {
  if ($("#speak-toggle").hasClass("button-checked")) {
    speak(current_word["word_diacritic"]);
  }
}

function speak(text) {
  var msg = new SpeechSynthesisUtterance();
  msg.text = text;
  msg.lang = speech_voice;
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

function clicked_speak() {
  speak(current_word["word_diacritic"]);
}

function increase_word() {
  add_word_to_arrays(current_word);
}

function decrease_word() {
  remove_word_from_arrays();
}

function remove_word_from_arrays() {
  // remove from all words
  var index = all_words.indexOf(current_word);
  if (index !== -1) {
    all_words.splice(index, 1);
  }

  // remove from XXXX_words
  XXXX_words.splice(current_word_index, 1);

  // Get the next word now.
  current_word = null;
  word_state = 2;
  current_word_index = current_word_index - 1;
  clicked_next_word();
}

function add_word_to_arrays(word) {
  slice_index = getRandomInt(largest_word_index, XXXX_words.length);
  XXXX_words.splice(slice_index, 0, word);
  all_words.push(word);
  console.log(XXXX_words);
  console.log(all_words);
}

function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

$(document).ready(function () {
  all_words = Array.from(original_words);
  XXXX_words = Array.from(original_words);
  shuffleArray(XXXX_words);
  clicked_next_word();

  $(function () {
    $(window).keydown(function (e) {
      if (!$("#edit-popup").is(":visible")) {
        var key = e.which;
        if (key == "32" || key == "13" || key == "39") {
          clicked_next_word();
        } else if (key == "37") {
          clicked_previous_word();
        } else if (key == "8") {
          decrease_word();
        } else if (key == "83" || key == "38") {
          increase_word();
        }
      }
    });
  });
});

async function clicked_update(rating) {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  clear_ratings();
  $("#button-ratifng-" + rating).addClass("rating-checked");

  await db.put("lemmas", { word: current_word["word"], rating: rating });
}

async function get_rating() {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  var res = await db.get("lemmas", current_word["word"]);
  if (res) {
    clear_ratings();
    rating = res.rating;
    $("#button-rating-" + rating).addClass("rating-checked");
  }
}

function clear_ratings() {
  $("#button-rating-" + 1).removeClass("rating-checked");
  $("#button-rating-" + 2).removeClass("rating-checked");
  $("#button-rating-" + 3).removeClass("rating-checked");
  $("#button-rating-" + 4).removeClass("rating-checked");
  $("#button-rating-" + 5).removeClass("rating-checked");
}

function show_edit_popup() {
  $("#popup-word").text(current_word["word"]);
  $("#existing-roots").text(current_word["user_roots"]);
  $("#existing-translations").text(current_word["user_translations"]);
  $(".popup").show();
}
function hide_edit_popup() {
  $(".popup").hide();
}

function update_root() {
  let new_root = document.getElementById("new_root").value;
  word = current_word["word"];

  data = {
    new_user_root: new_root,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + word + "/",
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

function update_translation() {
  let new_translation = document.getElementById("new_translation").value;
  word = $("#popup-word").text();

  data = {
    new_user_translation: new_translation,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + word + "/",
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

function removeWordFromWords(word) {
  XXXX_words = XXXX_words.filter(function (value) {
    return value["word"] !== word;
  });
  all_words = all_words.filter(function (value) {
    return value["word"] !== word;
  });
}
