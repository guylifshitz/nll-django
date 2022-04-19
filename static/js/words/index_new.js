async function show_ratings() {
  const db = await idb.openDB("news-lang-learn", 1, {
    upgrade(db) {
      const store = db.createObjectStore("lemmas", {
        keyPath: "word",
      });
    },
  });

  words.forEach(async (word) => {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      rating = res.rating;
      $("#button-rating-" + rating + "-" + word["word"]).addClass(
        "rating-checked"
      );
    }
  });
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

  words.forEach(async (word) => {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"]).prop('checked', true);
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

  words.forEach(async (word) => {
    res = await db.get("lemmas", word["word"]);
    if (res) {
      word_rating = res.rating;
      if (filter_rating == word_rating) {
        $("#select-word-" + word["word"]).prop('checked', false);
      }
    }
  });
}

function clear_selection(){
  $(".select-word-checkbox").prop('checked', false);
}

function select_all(){
  $(".select-word-checkbox").prop('checked', true);
}

$(document).ready(function () {
  show_ratings();
});
