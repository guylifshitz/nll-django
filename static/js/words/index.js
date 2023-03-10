var words;
var words_to_show_dict;

async function get_db() {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
      store.createIndex("rating", "rating");
    },
  });
  return db;
}

async function initialize_ratings() {
  const db = await get_db();

  for (const word of words) {
    // TODO handle better the escpaing of '
    res = await db.get("lemmas", word["word"]);
    if (res) {
      rating = res.rating;
      $(
        "#button-rating-" + rating + "-" + word["word"].replace("'", "\\'")
      ).addClass("rating-checked");
      $("#select-word-" + word["word"].replace("'", "\\'")).attr(
        "rating",
        rating
      );
      monitor_checkboxes_rating();
    }
  }
}

function clear_ratings(word) {
  for (let rating = 1; rating <= 5; rating++) {
    $("#button-rating-" + rating + "-" + word).removeClass("rating-checked");
  }
}

async function clicked_update(word, rating) {
  const db = await get_db();

  clear_ratings(word);
  $("#button-rating-" + rating + "-" + word).addClass("rating-checked");

  $("#select-word-" + word).attr("rating", rating);

  monitor_checkboxes_rating();
  await db.put("lemmas", { word: word, rating: rating });
}

async function select_by_filter(filter_rating) {
  const db = await get_db();

  if (filter_rating === 0) {
    select_unrated();
  }
  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"])
          .prop("checked", true)
          .change();
      }
    }
  }
  hide_unselected();
}

async function select_unrated() {
  const db = await get_db();

  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    word_has_rating = false;
    if (res) {
      word_has_rating = true;
    }
    if (!word_has_rating) {
      $("#select-word-" + word["word"])
        .prop("checked", true)
        .change();
    }
  }
  hide_unselected();
}

async function deselect_by_filter(filter_rating) {
  const db = await get_db();

  if (filter_rating === 0) {
    deselect_unrated();
  }

  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"])
          .prop("checked", false)
          .change();
      }
    }
  }
  hide_unselected();
}

async function deselect_unrated() {
  const db = await get_db();

  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    word_has_rating = false;
    if (res) {
      word_has_rating = true;
    }
    if (!word_has_rating) {
      $("#select-word-" + word["word"])
        .prop("checked", false)
        .change();
    }
  }
  hide_unselected();
}

function clear_selection() {
  $(".select-word-checkbox").prop("checked", false).change();
  hide_unselected();
}

function select_all() {
  $(".select-word-checkbox").prop("checked", true).change();
  hide_unselected();
}

async function import_word_ratings() {
  let input = document.createElement("input");
  input.type = "file";
  input.onchange = onChange;
  input.click();

  function onChange(event) {
    var reader = new FileReader();
    reader.onload = onReaderLoad;
    reader.readAsText(event.target.files[0]);
  }

  function onReaderLoad(event) {
    console.log(event.target.result);
    var obj = JSON.parse(event.target.result);
    add_ratings(obj);
  }

  async function add_ratings(ratings) {
    const db = await idb.openDB("news-lang-learn", 1);
    console.log(ratings);
    for (var i = 0; i < ratings.length; i++) {
      rating = ratings[i];
      db.put("lemmas", { word: rating["word"], rating: rating["rating"] });
    }
  }
}

async function export_word_ratings() {
  const db = await idb.openDB("news-lang-learn", 1);
  var ratings = await db.getAll("lemmas");
  download("word-ratings.json", JSON.stringify(ratings));
}

function download(filename, text) {
  var pom = document.createElement("a");
  pom.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(text)
  );
  pom.setAttribute("download", filename);

  if (document.createEvent) {
    var event = document.createEvent("MouseEvents");
    event.initEvent("click", true, true);
    pom.dispatchEvent(event);
  } else {
    pom.click();
  }
}

$(document).ready(function () {
  words = JSON.parse(document.getElementById("words-data").textContent);
  words_to_show_dict = JSON.parse(
    document.getElementById("words_to_show_dict-data").textContent
  );

  initialize_ratings();
  monitor_checkboxes();

  var today = new Date().toISOString().split("T")[0];
  var prev_day = new Date();
  prev_day.setDate(prev_day.getDate() - 7);
  prev_day = prev_day.toISOString().split("T")[0];

  $("#start-date").val(prev_day);
  $("#end-date").val(today);

  $("#ART_FORM").submit(function (e) {
    console.log("SUBmIt");
    submit_articles_form(this);
    return false;
  });
});

async function submit_articles_form(form) {
  await set_articles_submit_json();
  form.submit();
}

async function set_articles_submit_json() {
  const db = await get_db();

  const r = db.transaction("lemmas").store.index("rating");
  var practice_words = [];
  for (let rating = 1; rating <= 5; rating++) {
    if ($("#select-practice-rating-" + rating).is(":checked")) {
      practice_words.push.apply(practice_words, await r.getAllKeys(rating));
    }
  }

  if ($("#select-practice-by-selected").is(":checked")) {
    $(".select-word-checkbox:checked").each(function () {
      practice_words.push($(this).val());
    });
  }
  practice_words = JSON.stringify(practice_words);
  $("#practice_words").attr("value", practice_words);
  console.log(practice_words);
  var known_words2 = [];
  known_words2 = await db.getAllKeys("lemmas");

  if ($("#include-unrated").is(":checked")) {
    $(".select-word-checkbox").each(function () {
      known_words2.push($(this).val());
    });
  }

  known_words2 = known_words2.filter(function (value, index, arr) {
    return !practice_words.includes(value);
  });

  known_words2 = JSON.stringify(known_words2);
  $("#known_words").attr("value", known_words2);
}

function xxx(url, csrfToken) {
  var parameters = {};
  parameters["csrfmiddlewaretoken"] = csrfToken;

  parameters["test-1"] = get_known_words();
  // parameters["word"] = { adas: 122 };
  console.log(parameters);
  sendData(url, parameters);
}

async function get_known_words() {
  var practice_words = [];
  $(".select-word-checkbox:checkbox:checked").each(function (checkbox) {
    practice_words.push(this.value);
  });

  const db = await get_db();

  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      if (practice_words.includes(res[word["word"]])) {
        rating_text = "PRACTICE";
      } else if (res["rating"] == 5) {
        rating_text = "KNOWN";
      } else {
        rating_text = "SEEN";
      }
      output.push([word["word"], rating_text]);
    }
  }
}

function sendData(url, parameters) {
  const form = document.createElement("form");
  form.method = "post";
  form.action = url;
  document.body.appendChild(form);

  for (const key in parameters) {
    const formField = document.createElement("input");
    formField.type = "hidden";
    formField.name = key;
    formField.value = parameters[key];

    form.appendChild(formField);
  }
  form.submit();
}

function monitor_checkboxes() {
  $(".select-word-checkbox").change(function () {
    if ($(this).is(":checked")) {
      $(this).parent().parent().addClass("word-line-selected");
    } else {
      $(this).parent().parent().removeClass("word-line-selected");
    }

    if (
      $(".select-word-checkbox:checked").length ==
      $(".select-word-checkbox").length
    ) {
      $("#select-deselect-all").attr("checked", true);
      $("#select-deselect-all").prop("checked", true);
      $("#select-deselect-all").prop("indeterminate", false);
      $("#select-deselect-all").attr("onclick", "clear_selection()");
    } else if ($(".select-word-checkbox:checked").length == 0) {
      $("#select-deselect-all").attr("checked", false);
      $("#select-deselect-all").prop("checked", false);
      $("#select-deselect-all").prop("indeterminate", false);
      $("#select-deselect-all").attr("onclick", "select_all()");
    } else {
      $("#select-deselect-all").attr("checked", false);
      $("#select-deselect-all").prop("checked", false);
      $("#select-deselect-all").prop("indeterminate", true);
      $("#select-deselect-all").attr("onclick", "select_all()");
    }
  });
}

function monitor_checkboxes_rating() {
  for (let rating = 0; rating <= 5; rating++) {
    let num_words_with_rating = $(
      ".select-word-checkbox[rating='" + rating + "']"
    ).length;

    $(".select-word-checkbox[rating='" + rating + "']")
      .off("change.rating")
      .on("change.rating", function () {
        update_select_all_rating_checkbox(rating, num_words_with_rating);
      });

    update_select_all_rating_checkbox(rating, num_words_with_rating);
  }
}

function update_select_all_rating_checkbox(rating, num_words_with_rating) {
  if (num_words_with_rating == 0) {
    $("#select-deselect-rating-" + rating).prop("disabled", true);
  } else {
    $("#select-deselect-rating-" + rating).prop("disabled", false);
    if (
      $(".select-word-checkbox[rating='" + rating + "']:checked").length ==
      num_words_with_rating
    ) {
      $("#select-deselect-rating-" + rating).attr("checked", true);
      $("#select-deselect-rating-" + rating).prop("checked", true);

      $("#select-deselect-rating-" + rating).prop("indeterminate", false);

      $("#select-deselect-rating-" + rating).attr(
        "onclick",
        "deselect_by_filter(" + rating + ")"
      );
    } else if (
      $(".select-word-checkbox[rating='" + rating + "']:checked").length == 0
    ) {
      $("#select-deselect-rating-" + rating).attr("checked", false);
      $("#select-deselect-rating-" + rating).prop("checked", false);
      $("#select-deselect-rating-" + rating).prop("indeterminate", false);
      $("#select-deselect-rating-" + rating).attr(
        "onclick",
        "select_by_filter(" + rating + ")"
      );
    } else {
      $("#select-deselect-rating-" + rating).attr("checked", false);
      $("#select-deselect-rating-" + rating).prop("checked", false);
      $("#select-deselect-rating-" + rating).prop("indeterminate", true);
      $("#select-deselect-rating-" + rating).attr(
        "onclick",
        "select_by_filter(" + rating + ")"
      );
    }
  }
}
function hide_popups() {
  $(".popup").hide();
}
function show_articles_popup() {
  $("#articles-popup").show();
  let words_selected_count = $(".select-word-checkbox:checked").length;
  $("#words-selected-count").text(words_selected_count);
}

function hide_unselected() {
  // TODO move this somewhere else
  let words_selected_count = $(".select-word-checkbox:checked").length;
  $("#selcted_count").text(words_selected_count);

  if ($("#filter-unselected").prop("checked")) {
    $(".select-word-checkbox:not(checked)").parent().parent().parent().hide();
    $(".select-word-checkbox:checked").parent().parent().parent().show();
    // $("#filter-unselected").attr("onclick", "show_unselected()");
  } else {
    $(".select-word-checkbox").parent().parent().parent().show();
    $("#filter-unselected").attr("onclick", "hide_unselected()");
  }
}

function show_edit_popup(word) {
  $("#popup-word").text(word.word);
  $("#root").text(word.root);
  $("#translation").text(word.translation);
  $("#existing-translations").text(word.user_translations);

  $("#new_translation").val("");
  $("#new_root").val("");

  $("#edit-popup").show();

  var datalist = $("#existing_translations_list");
  datalist.empty();
  $("#existing-translations").empty();
  word.user_translations.forEach(function (t) {
    $("#existing-translations").append(
      "<div class='existing-entry'>" + t + "</div>"
    );
    datalist.append("<option value='" + t + "'>");
  });

  var datalist = $("#existing_roots_list");
  datalist.empty();
  $("#existing-roots").empty();
  word.user_roots.forEach(function (r) {
    $("#existing-roots").append("<div class='existing-entry'>" + r + "</div>");
    datalist.append("<option value='" + r + "'>");
  });
}

function hide_edit_popup() {
  $(".popup").hide();
}

async function examples_word(practice_word, token) {
  const db = await get_db();

  var practice_words = [practice_word];
  var known_words2 = [];
  known_words2 = await db.getAllKeys("lemmas");
  known_words2 = known_words2.filter(function (value, index, arr) {
    return !practice_words.includes(value);
  });

  var form = document.createElement("form");

  form.setAttribute("method", "post");
  form.setAttribute("target", "_blank");
  form.setAttribute("action", "articles/index");

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

function show_context_menu(element) {
  var rect = element.getBoundingClientRect();
  console.log(rect);
  $("#context-menu").show();
  $("#context-menu").css("left", element.offsetLeft + 15);
  $("#context-menu").css("top", element.offsetTop + 5);
  $("#context-menu").attr("word", $(element).attr("word"));
}

window.onclick = function (event) {
  if (
    !(
      event.target.matches("#context-menu") ||
      event.target.matches(".show_context_menu")
    )
  ) {
    console.log("hide ");
    $("#context-menu").hide();
  }
};

function context_menu_open_definition(element, language) {
  window.open(
    "https://en.wiktionary.org/wiki/" +
      $("#context-menu").attr("word") +
      "#" +
      language
  );
}

function context_menu_examples_word(element, token) {
  examples_word($("#context-menu").attr("word"), token);
}

function context_menu_edit_word() {
  show_edit_popup(words_to_show_dict[$("#context-menu").attr("word")]);
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

function update_root() {
  let new_root = document.getElementById("new_root").value;
  word = $("#popup-word").text();

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
      $("#" + word + "-root").text(new_root);
    })
    .fail(function () {
      alert("error");
    })
    .always(function () {
      // alert("complete");
    });
}
