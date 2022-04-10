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
  if (element.className == "neutral") {
    await db.put("bllooop", { rating: 1, word: word });
  }
  if (element.className == "super-happy") {
    await db.put("bllooop", { rating: 2, word: word });
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
        $("#neutral-" + word["index"]).click();
        console.log(res);
      } else if (res["rating"] == 2) {
        $("#super-happy-" + word["index"]).click();
        console.log(res);
      }
    }
  });
}
