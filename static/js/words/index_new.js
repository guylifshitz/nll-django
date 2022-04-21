async function initialize_ratings() {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  for (const word of words) {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      rating = res.rating;
      $("#button-rating-" + rating + "-" + word["word"]).addClass(
        "rating-checked"
      );
      $("#select-word-" + word["word"]).attr("rating", rating);
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
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  clear_ratings(word);
  $("#button-rating-" + rating + "-" + word).addClass("rating-checked");

  $("#select-word-" + word).attr("rating", rating);

  monitor_checkboxes_rating();
  await db.put("lemmas", { word: word, rating: rating });
}

async function select_by_filter(filter_rating) {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  // do we need to change this to a blocking for?
  words.forEach(async (word) => {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"])
          .prop("checked", true)
          .change();
      }
    }
  });
}

async function deselect_by_filter(filter_rating) {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  // do we need to change this to a blocking for?
  words.forEach(async (word) => {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"])
          .prop("checked", false)
          .change();
      }
    }
  });
}

function clear_selection() {
  $(".select-word-checkbox").prop("checked", false).change();
}

function select_all() {
  $(".select-word-checkbox").prop("checked", true).change();
}

async function export_words_to_csv() {
  var practice_words = [];
  $(".select-word-checkbox:checkbox:checked").each(function (checkbox) {
    practice_words.push(this.value);
  });

  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  // do we need to change this to a blocking for?
  words.forEach(async (word) => {
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
  });
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
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  var practice_words = [];
  $(".select-word-checkbox:checked").each(function () {
    practice_words.push($(this).val());
  });
  practice_words = JSON.stringify(practice_words);
  $("#practice_words").attr("value", practice_words);

  var known_words2 = [];
  known_words2 = await db.getAllKeys("lemmas");

  console.log($("#include-unrated").is(":checked"));
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
  console.log("XXX");
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

  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  // do we need to change this to a blocking for?
  words.forEach(async (word) => {
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
  });
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
  for (let rating = 1; rating <= 5; rating++) {
    let num_words_with_rating = $(
      ".select-word-checkbox[rating='" + rating + "']"
    ).length;

    $(".select-word-checkbox[rating='" + rating + "']")
      .off("change.rating")
      .on("change.rating", function () {
        doop(rating, num_words_with_rating);
      });

    doop(rating, num_words_with_rating);
  }
}

function doop(rating, num_words_with_rating) {
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
  $("#words-selected-count").text($(".select-word-checkbox:checked").length);
}
