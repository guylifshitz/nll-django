var words;
var words_to_show_dict;
var user_word_ratings;

async function initialize_ratings() {
  for (const word of words) {
    // TODO handle better the escpaing of '
    rating = word.rating;
    console.log(word);
    console.log(word.rating);
    console.log(
      "#" +
        $.escapeSelector(
          "button-rating-" + rating + "-" + word["word"].replace("'", "\\'")
        )
    );
    $(
      "#" +
        $.escapeSelector(
          "button-rating-" + rating + "-" + word["word"].replace("'", "\\'")
        )
    ).addClass("rating-checked");
    $(
      "#" + $.escapeSelector("select-word-" + word["word"].replace("'", "\\'"))
    ).attr("rating", rating);
    monitor_checkboxes_rating();
  }
}

function clear_ratings(word) {
  for (let rating = 1; rating <= 5; rating++) {
    $(
      "#" + $.escapeSelector("button-rating-" + rating + "-" + word)
    ).removeClass("rating-checked");
  }
}

async function clicked_update(word, rating) {
  clear_ratings(word);
  $("#" + $.escapeSelector("button-rating-" + rating + "-" + word)).addClass(
    "rating-checked"
  );

  $("#" + $.escapeSelector("select-word-" + word)).attr("rating", rating);

  monitor_checkboxes_rating();
  update_rating(word, rating);

  for (const w of words) {
    word_text = w.word;
    if (word_text === word) {
      w.rating = rating;
    }
  }
}

async function select_by_filter(filter_rating) {
  if (filter_rating === 0) {
    select_unrated();
  }
  for (const word of words) {
    word_rating = word.rating;
    if (filter_rating == word_rating) {
      $("#" + $.escapeSelector("select-word-" + word["word"]))
        .prop("checked", true)
        .change();
    }
  }
  hide_unselected();
}

async function select_unrated() {
  for (const word of words) {
    word_has_rating = word.rating !== null;
    if (!word_has_rating) {
      $("#" + $.escapeSelector("select-word-" + word["word"]))
        .prop("checked", true)
        .change();
    }
  }
  hide_unselected();
}

async function deselect_by_filter(filter_rating) {
  if (filter_rating === 0) {
    deselect_unrated();
  }

  for (const word of words) {
    word_rating = word.rating;
    if (filter_rating == word_rating) {
      $("#" + $.escapeSelector("select-word-" + word["word"]))
        .prop("checked", false)
        .change();
    }
  }
  hide_unselected();
}

async function deselect_unrated() {
  for (const word of words) {
    word_has_rating = false;
    word_has_rating = word.rating !== null;
    if (!word_has_rating) {
      $("#" + $.escapeSelector("select-word-" + word["word"]))
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
  user_word_ratings = JSON.parse(
    document.getElementById("user_word_ratings-data").textContent
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
    submit_articles_form(this);
    return false;
  });
});

async function submit_articles_form(form) {
  await set_articles_submit_json();
  form.submit();
}

async function set_articles_submit_json() {
  var practice_words = [];
  for (let rating = 1; rating <= 5; rating++) {
    if ($("#select-practice-rating-" + rating).is(":checked")) {
      practice_words.push.apply(
        practice_words,
        user_word_ratings
          .filter((wordrating) => wordrating["rating"] === rating)
          .map((item) => item["word"])
      );
    }
  }
  if ($("#select-practice-by-selected").is(":checked")) {
    $(".select-word-checkbox:checked").each(function () {
      practice_words.push($(this).val());
    });
  }
  practice_words = JSON.stringify(practice_words);
  $("#practice_words").attr("value", practice_words);

  var known_words2 = user_word_ratings.map((item) => item["word"]);

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
  sendData(url, parameters);
}

async function get_known_words() {
  var practice_words = [];
  $(".select-word-checkbox:checkbox:checked").each(function (checkbox) {
    practice_words.push(this.value);
  });

  for (const word of words) {
    if (word["word"] in user_word_ratings) {
      if (practice_words.includes(word["word"])) {
        rating_text = "PRACTICE";
      } else if (word_user_ratings[word["word"]] === 5) {
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
    update_words_selected_counter();
    hide_unselected();
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

function submit_form(form_id) {
  $("#" + form_id).submit();
}

function hide_unselected() {
  update_words_selected_counter();
  if ($("#filter-unselected").prop("checked")) {
    $(".select-word-checkbox:not(checked)").parent().parent().parent().hide();
    $(".select-word-checkbox:checked").parent().parent().parent().show();
    // $("#filter-unselected").attr("onclick", "show_unselected()");
  } else {
    $(".select-word-checkbox").parent().parent().parent().show();
    $("#filter-unselected").attr("onclick", "hide_unselected()");
  }
}

function update_words_selected_counter() {
  let words_selected_count = $(".select-word-checkbox:checked").length;
  $("#selcted_count").text(words_selected_count);
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
  var practice_words = [practice_word];
  var known_words2 = user_word_ratings.map((item) => item["word"]);
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
    console.log("hide");
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

function context_menu_show_word() {
  html_txt = $("#context-menu").attr("word");
  window.open("/words/word?word=" + html_txt);
}

function update_translation() {
  let new_translation = document.getElementById("new_translation").value;
  word = $("#popup-word").text();

  data = {
    new_user_translation: new_translation,
    user_id: user_id,
  };
  $.ajax({
    type: "PATCH",
    url: "http://localhost:8001/api/words/" + word + "/",
    data: JSON.stringify(data),
    processData: false,
    contentType: "application/json",
  })
    .done(function () {
      $("#" + word + "-translation").text(new_translation);
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
      $("#" + word + "-root").text(new_root);
      alert("success");
    })
    .fail(function () {
      alert("error");
    })
    .always(function () {
      // alert("complete");
    });
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

function submit_filter_form() {
  let form_data = new FormData(document.querySelector("#filter-form"));
  let form_str = new URLSearchParams(form_data).toString();

  var getUrl = window.location;
  window.location.href =
    getUrl.protocol +
    "//" +
    getUrl.host +
    "/" +
    getUrl.pathname.split("/")[1] +
    "?" +
    form_str;
}

function toggle_visible_words() {
  var is_checked = $("#filter-unselected").prop("checked");

  if (is_checked) {
    $("#filter-unselected-icon").removeClass("fa-eye-slash");
    $("#filter-unselected-icon").addClass("fa-eye");
  } else {
    $("#filter-unselected-icon").removeClass("fa-eye");
    $("#filter-unselected-icon").addClass("fa-eye-slash");
  }

  $("#filter-unselected").prop("checked", !is_checked);
  hide_unselected();
}
