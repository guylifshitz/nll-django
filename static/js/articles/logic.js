var speech_rate = 0.7;

function position_tooltips() {
  var tooltips = $(".word_tooltip");
  $.each(tooltips, function (index, tooltip) {
    var box = tooltip.previousElementSibling.getBoundingClientRect();
    tooltip.style.position = "absolute";
    tooltip.style.top = box.top + 60 + window.scrollY + "px";
    tooltip.style.left = box.left + (box.right - box.left) / 2 - 60 + "px";
  });
}

function speak_title_helper(button) {
  div = $(button).parent().parent();
  speak_title(div);
  button.classList.toggle("button-active");
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
  msg.rate = speech_rate;
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
    $(".button_speak").removeClass("button-active");
  };
}

function speak(text) {
  var msg = new SpeechSynthesisUtterance();
  msg.text = text;
  msg.lang = speech_voice;
  msg.rate = speech_rate;
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

window.onload = position_tooltips;

$(document).ready(function () {
  $(function () {
    $(window).keydown(function (e) {
      var key = e.which;
      if (key == 61) {
        speech_rate += 0.1;
        console.log("speech_rate: ", speech_rate.toFixed(1));
      }
      if (key == 173) {
        speech_rate -= 0.1;
        console.log("speech_rate: ", speech_rate.toFixed(1));
      }
    });
  });

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
    language = window.location.pathname.split("/")[1];
    if (event.altKey) {
      html_txt = $(event.target).attr("lemma");
      window.open("/" + language + "/words/word?word=" + html_txt);

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

// TODO method not used and hard coded already.
function open_word_details_page(element) {
  language = window.location.pathname.split("/")[1];
  html_txt = $(element).attr("lemma");
  window.open("/" + language + "/words/word?word=" + html_txt);
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
    url: "/api/rating/",
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
    .fail(function () { })
    .always(function () { });
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

function toggle_section(button, section) {

  let section_element = button.parentElement.parentElement.getElementsByClassName(section)[0];
  let first_hidden = section_element.hidden;

  section_element.hidden = !first_hidden;
  if (first_hidden === true) {
    button.classList.add("button-active"); 
  } else {
    button.classList.remove("button-active");
  }
  position_tooltips();
  check_all_button_state(section);
}

function toggle_section_all(button, section_class, button_class){
  let sections = document.querySelectorAll(section_class)
  let buttons = document.querySelectorAll(button_class)
  let hidden = !button.classList.contains("button-active");
  if (hidden === true) {
    button.classList.add("button-active");
    sections.forEach(element => {
      element.hidden = false;
    });
    buttons.forEach(element => {
      element.classList.add("button-active");
    });
  } else {
    button.classList.remove("button-active");
    sections.forEach(element => {
      element.hidden = true;
    });
    buttons.forEach(element => {
      element.classList.remove("button-active");
    });
  }  
  position_tooltips();
}

function check_all_button_state(section_class){
  let sections = document.querySelectorAll("."+section_class)
  console.log(sections);
  let any_hidden = Array.from(sections).some(element => {
    console.log(element.hidden);
    return element.hidden == true;
  });
  section_class = section_class.replace(".", "")
  button_name = "button_" + section_class + "_all"
  if (any_hidden){
    document.getElementById(button_name).classList.remove("button-active");
  }else{
    document.getElementById(button_name).classList.add("button-active");
  }
}