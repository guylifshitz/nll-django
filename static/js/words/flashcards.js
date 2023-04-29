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
var original_words;

var top_word;
var bottom_word;
var root;
var flexions;
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

  flexions = pretty_flexions(current_word["flexions"]);

  if (flexions === "") {
    flexions = "-m-,-";
  }

  $("#new_root").val("");
  $("#new_translation").val("");
}
function pretty_flexions(flexions) {
  let arr = [];
  for (var key in flexions) {
    if (flexions.hasOwnProperty(key)) {
      arr.push(key + "&nbsp;&nbsp;&nbsp;&nbsp;" + flexions[key] + "<br>  ");
    }
  }
  arr = "<br>" + arr.join("   ");
  return arr;
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
  $("#word-flexions").text("---");

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
  $("#word-flexions").html(flexions);
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
  $("#open-pealim").attr(
    "href",
    "https://www.pealim.com/search/?q=" + current_word["word"]
  );
  //TODO it would be nice if the articles config could take the word as a param, and know that that is the word we want to show
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const language = urlParams.get("language");
  var base_url = window.location.origin + "/articles/config";
  var seen_cutoff = Math.max(current_word["index"] + 1, 500);
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

function toggle_flexions(element) {
  toggle_checked(element);
  $("#word-flexions").toggle();
  refresh_ui(word_state);
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
  original_words = JSON.parse(
    document.getElementById("original_words-data").textContent
  );
  all_words = Array.from(original_words);
  XXXX_words = Array.from(original_words);
  user_word_ratings = JSON.parse(
    document.getElementById("user_word_ratings-data").textContent
  );
  shuffleArray(XXXX_words);
  clicked_next_word();

  $(function () {
    $(window).keydown(function (e) {
      if (!$("#edit-popup").is(":visible")) {
        var key = e.which;
        console.log(key);
        if (key == "32" || key == "13" || key == "39") {
          clicked_next_word();
        } else if (key == "37") {
          clicked_previous_word();
        } else if (key == "8") {
          decrease_word();
        } else if (key == "90" || key == "18") {
          clicked_speak();
        } else if (key == "83" || key == "38") {
          increase_word();
        } else if (key == "49") {
          clicked_update(1);
        } else if (key == "50") {
          clicked_update(2);
        } else if (key == "51") {
          clicked_update(3);
        } else if (key == "52") {
          clicked_update(4);
        } else if (key == "53") {
          clicked_update(5);
        } else if (key == "81") {
          clicked_update(1);
        } else if (key == "87") {
          clicked_update(2);
        } else if (key == "69") {
          clicked_update(3);
        } else if (key == "82") {
          clicked_update(4);
        } else if (key == "84") {
          clicked_update(5);
        }
      }
    });
  });
});

// async function clicked_update(rating) {
//   const db = await idb.openDB("news-lang-learn", 1, {
//     upgrade(db) {
//       const store = db.createObjectStore("lemmas", {
//         keyPath: "word",
//       });
//     },
//   });

//   clear_ratings();
//   $("#button-rating-" + rating).addClass("rating-checked");

//   await db.put("lemmas", { word: current_word["word"], rating: rating });
// }

async function clicked_update(rating) {
  clear_ratings();
  $("#button-rating-" + rating).addClass("rating-checked");
  update_rating(current_word["word"], rating);
  current_word.rating = rating;
}

function update_rating(word, rating) {
  data = {
    find_text: word,
    new_rating: rating,
  };
  $.ajax({
    type: "POST",
    url: "http://localhost:8001/api/rating/",
    data: JSON.stringify(data),
    processData: false,
    contentType: "application/json",
    headers: {
      Authorization: "Token " + user_auth_token,
    },
  })
    .done(function () {
      //# TODO move the update gui here
    })
    .fail(function () {})
    .always(function () {});
}

// async function get_rating() {
// const db = await idb.openDB("news-lang-learn", 1, {
//   upgrade(db) {
//     const store = db.createObjectStore("lemmas", {
//       keyPath: "word",
//     });
//   },
// });

// var res = await db.get("lemmas", current_word["word"]);
// if (res) {
// clear_ratings();
// rating = res.rating;
// $("#button-rating-" + rating).addClass("rating-checked");
// }
// }
async function get_rating() {
  clear_ratings();
  rating = current_word.rating;
  $("#button-rating-" + rating).addClass("rating-checked");
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
    username: user_username,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + word + "/",
    data: JSON.stringify(data),
    processData: false,
    contentType: "application/json",
  })
    .done(function () {
      // TODO update the root in the flashcards.
      current_word["root"] = new_root;
      $("#word-root").text(new_root);
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
    username: user_username,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + word + "/",
    data: JSON.stringify(data),
    processData: false,
    contentType: "application/json",
  })
    .done(function () {
      current_word["translation"] = new_translation;

      if ($("#swap-top-bottom").hasClass("button-checked")) {
        $("#word-top").text(current_word["translation"]);
      } else {
        $("#word-bottom").text(current_word["translation"]);
      }

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

function show_similar_roots() {
  $.ajax({
    type: "GET",
    url: "http://localhost:8001/api/similar_words/" + word + "/",
    processData: false,
    contentType: "application/json",
  }).done(function (res) {
    alert(JSON.stringify(res["similar_roots"], null, 2));
  });
}

function show_similar_words() {
  $.ajax({
    type: "GET",
    url: "http://localhost:8001/api/similar_words/" + word + "/",
    processData: false,
    contentType: "application/json",
  }).done(function (res) {
    alert(JSON.stringify(res["similar_words"], null, 2));
  });
}

function context_menu_examples_word(element, token) {
  examples_word(current_word["word"], token);
}

async function examples_word(practice_word, token) {
  var practice_words = [practice_word];
  var known_words2 = [];
  if (user_word_ratings !== "") {
    var known_words2 = user_word_ratings.map((item) => item["word"]);
  }
  known_words2 = known_words2.filter(function (value, index, arr) {
    return !practice_words.includes(value);
  });

  var form = document.createElement("form");

  form.setAttribute("method", "post");
  form.setAttribute("target", "_blank");
  form.setAttribute("action", "../../articles/index");

  var token_input = document.createElement("input");
  token_input.setAttribute("type", "hidden");
  token_input.setAttribute("name", "csrfmiddlewaretoken");
  token_input.setAttribute("value", token);
  form.appendChild(token_input);

  var practice_words_input = document.createElement("input");
  practice_words_input.setAttribute("type", "hidden");
  practice_words_input.setAttribute("name", "practice_words");
  practice_words_input.setAttribute("value", JSON.stringify(practice_words));
  form.appendChild(practice_words_input);

  var known_words_input = document.createElement("input");
  known_words_input.setAttribute("type", "hidden");
  known_words_input.setAttribute("name", "known_words");
  known_words_input.setAttribute("value", JSON.stringify(known_words2));
  form.appendChild(known_words_input);

  var start_date_input = document.createElement("input");
  start_date_input.setAttribute("type", "hidden");
  start_date_input.setAttribute("name", "start_date");
  start_date_input.setAttribute("value", "2020-01-01");
  form.appendChild(start_date_input);

  var sort_by_practice_input = document.createElement("input");
  sort_by_practice_input.setAttribute("type", "hidden");
  sort_by_practice_input.setAttribute("name", "sort_by_practice_only");
  sort_by_practice_input.setAttribute("value", "NOTESET");
  form.appendChild(sort_by_practice_input);

  document.body.appendChild(form);
  form.submit();
}
