function position_tooltips() {
  var tooltips = $(".word_tooltip");
  $.each(tooltips, function (index, tooltip) {
    var box = tooltip.previousElementSibling.getBoundingClientRect();
    tooltip.style.position = "absolute";
    tooltip.style.top = box.top + 60 + window.scrollY + "px";
    tooltip.style.left = box.left + (box.right - box.left) / 2 - 60 + "px";
  });
}

function show_full_translation(element) {
  $(element).parent().parent().find(".title_translation").toggle();
  position_tooltips();
}

function speak_title_helper(element) {
  div = $(element).parent().parent();
  speak_title(div);
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
    speakElement.find("#" + idOfChild).css("color", "blue");
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

function show_partial_translation(element) {
  $(element).parent().parent().find(".title_mix").toggle();
  position_tooltips();
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

  position_tooltips();
  window.addEventListener("resize", position_tooltips, true);

  $(".word").click(function (event) {
    if (event.altKey) {
      html_txt = $(event.target).attr("lemma");
      window.open("/words/word?word=" + html_txt);

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

function open_word_details_page(element) {
  html_txt = $(element).attr("lemma");
  window.open("/words/word?word=" + html_txt);
}

function clicked_source(element) {
  $(".card")
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
  // const db = await get_db();

  $("#rating_button_0").css("background-color", "#bad3da");
  $("#rating_button_1").css("background-color", "#bad3da");
  $("#rating_button_2").css("background-color", "#bad3da");
  $("#rating_button_3").css("background-color", "#bad3da");

  $("#rating_button_" + rating).css("background-color", "red");

  var word = $("#word_correction_word").text();
  // await db.put("lemmas", { rating: rating, word: word });
  update_rating(word, rating + 1);
}

function update_rating(word, rating) {
  data = {
    word_text: word,
    rating: rating,
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
