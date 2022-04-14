async function clicked_rb(element) {
  const db = await idb.openDB("testDB", 1, {
    upgrade(db) {
      const store = db.createObjectStore("bllooop", {
        keyPath: "word",
      });
    },
  });

  var word = element.getAttribute("word");
  console.log(word);
  if (element.className == "super-sad") {
    await db.put("bllooop", { rating: 0, word: word });
  }
  if (element.className == "sad") {
    await db.put("bllooop", { rating: 1, word: word });
  }
  if (element.className == "neutral") {
    await db.put("bllooop", { rating: 2, word: word });
  }
  if (element.className == "super-happy") {
    await db.put("bllooop", { rating: 3, word: word });
  }
}

async function clicked_update(element) {
  const db = await idb.openDB("testDB", 1, {
    upgrade(db) {
      const store = db.createObjectStore("bllooop", {
        keyPath: "word",
      });
    },
  });

  words.forEach(async (word) => {
    console.log(" a");
    res = await db.get("bllooop", word["word"]);
    if (res) {
      console.log(word);
      console.log(res);
      if (res["rating"] == 0) {
        $("#super-sad-" + word["index"]).click();
        console.log(res);
      } else if (res["rating"] == 1) {
        $("#sad-" + word["index"]).click();
        console.log(res);
      } else if (res["rating"] == 2) {
        $("#neutral-" + word["index"]).click();
        console.log(res);
      } else if (res["rating"] == 3) {
        $("#super-happy-" + word["index"]).click();
        console.log(res);
      }
    }
  });
}

async function export_words_to_csv() {
  const db = await idb.openDB("testDB", 1, {
    upgrade(db) {
      const store = db.createObjectStore("bllooop", {
        keyPath: "word",
      });
    },
  });

  var output = [];

  // words.forEach(async (word) => {
  for (const word of words) {
    res = await db.get("bllooop", word["word"]);
    if (res) {
      rating_text = "";
      if (res["rating"] == 0) {
        rating_text = "PRACTICE";
      } else if (res["rating"] == 1) {
        rating_text = "SEEN";
      } else if (res["rating"] == 2) {
        rating_text = "SEEN";
      } else if (res["rating"] == 3) {
        rating_text = "KNOWN";
      }
      output.push([word["word"], rating_text]);
    }
  }

  output_csv = "word,TYPE\r\n";
  output.forEach(function (rowArray) {
    let row = rowArray.join(",");
    output_csv += row + "\r\n";
  });

  console.log("output_csv");
  console.log(output_csv);
  download("words.csv", output_csv);
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
