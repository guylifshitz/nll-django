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

function position_tooltips() {
  var tooltips = $(".word_tooltip");
  $.each(tooltips, function (index, tooltip) {
    var box = tooltip.previousElementSibling.getBoundingClientRect();
    tooltip.style.position = "absolute";
    tooltip.style.top = box.top + 20 + window.scrollY + "px";
    tooltip.style.left = box.left + (box.right - box.left) / 2 - 50 + "px";
  });
}

$(document).ready(function () {
  function google_translate_word() {
    html_txt = $(event.target).attr("original_txt");

    var url =
      "https://translation.googleapis.com/language/translate/v2?key=AIzaSyDFM-_ShPiWSGtCtiDidNXa_CagmuM2Jk4";
    url += "&source=he";
    url += "&target=en";
    url += "&q=" + html_txt;
    $.get(url, function (data, status) {
      alert(html_txt + ":  " + data.data.translations[0].translatedText);
    });
  }

  function show_full_translation(event) {
    $(event.target).parent().parent().find(".title_translation").toggle();
    position_tooltips();
  }

  // Get the word of a string given the string and the index
  function getWordAt(str, pos) {
    // Perform type conversions.
    str = String(str);
    pos = Number(pos) >>> 0;

    // Search for the word's beginning and end.
    var left = str.slice(0, pos + 1).search(/\S+$/),
      right = str.slice(pos).search(/\s/);

    // The last word in the string is a special case.
    if (right < 0) {
      return str.slice(left);
    }
    // Return the word, using the located bounds to extract it from the string.
    return str.slice(left, right + pos);
  }

  function getWordIndexAtCharIndex(str, pos) {
    str = String(str);
    pos = Number(pos) >>> 0;

    text_so_far = str.slice(0, pos);
    num_words_so_far = text_so_far.split(" ").length;

    return num_words_so_far;
  }

  function speak_title(speakElement) {
    bigstring = "";
    speakElement
      .find(".title")
      .find(".word")
      .each(function (index, item) {
        console.log(item);
        bigstring += $(item).text() + " ";
      });

    var msg = new SpeechSynthesisUtterance();
    msg.text = bigstring;
    msg.lang = speech_voice;
    msg.rate = 0.7;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);

    msg.onboundary = function (event) {
      console.log(event.charIndex);
      console.log(getWordAt(bigstring, event.charIndex));

      word_idx = getWordIndexAtCharIndex(bigstring, event.charIndex);
      idOfChild = "word_" + word_idx;
      speakElement.find("#" + idOfChild).css("color", "white");
    };

    msg.onend = function (event) {
      $(".word").css("color", "black");
      console.log("DONE");
    };
  }

  function speak(text) {
    var msg = new SpeechSynthesisUtterance();
    msg.text = text;
    msg.lang = speech_voice;
    msg.rate = 0.5;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
  }

  function speak_title_helper(event) {
    div = $(event.target).parent().parent();
    speak_title(div);
  }

  function show_partial_translation(event) {
    $(event.target).parent().parent().find(".title_mix").toggle();
    position_tooltips();
  }

  $(".button_partial_translation").on("click", show_partial_translation);
  $(".button_full_translation").on("click", show_full_translation);

  $(".button_speak").on("click", speak_title_helper);

  position_tooltips();
  window.addEventListener("resize", position_tooltips, true);

  $(".word").click(function (event) {
    if (event.altKey) {
      html_txt = $(event.target).attr("lemma");
      show_edit_popup(html_txt);
      // google_translate_word();
    } else if (event.shiftKey) {
      html_txt = $(event.target).attr("original_txt");
      speak(html_txt);
    } else {
      Array.from(
        event.target.nextElementSibling.getElementsByClassName("mix_tooltip_2")
      ).forEach((tooltip2) => $(tooltip2).toggle());
    }
  });
});

function clicked_source(element) {
  $(".article")
    .filter('[feed_source="' + element.getAttribute("source") + '"]')
    .toggle(element.checked);

  position_tooltips();
}

function clicked_feed_name(element) {
  $(".article[feed_name*='" + element.getAttribute("feed_name") + "']").toggle(
    element.checked
  );

  position_tooltips();
}

async function clicked_update(rating) {
  const db = await get_db();

  $("#rating_button_0").css("background-color", "#bad3da");
  $("#rating_button_1").css("background-color", "#bad3da");
  $("#rating_button_2").css("background-color", "#bad3da");
  $("#rating_button_3").css("background-color", "#bad3da");

  $("#rating_button_" + rating).css("background-color", "red");

  var word = $("#word_correction_word").text();
  await db.put("lemmas", { rating: rating, word: word });
}

function show_edit_popup(word) {
  $("#word_correction_popup").show();
  $("#word_correction_word").text(word);
}
function hide_edit_popup() {
  $("#word_correction_popup").hide();
  $("#rating_button_0").css("background-color", "#bad3da");
  $("#rating_button_1").css("background-color", "#bad3da");
  $("#rating_button_2").css("background-color", "#bad3da");
  $("#rating_button_3").css("background-color", "#bad3da");
}
