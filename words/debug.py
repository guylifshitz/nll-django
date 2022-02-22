from fuzzywuzzy import fuzz
import pandas as pd
from pathlib import Path

def calculate_word_distance(row):

    idx = row.name
    dffs = []
    col_names = []
    for col in row.iteritems():
        col = col[0]
        col_names.append(col)
        dif = fuzz.partial_ratio(idx, col)
        dffs.append(dif)
    return pd.Series(dffs, index=col_names)


def calculate_word_distances(words):

    translations = {}
    for word in words:
        translations[word["word"]] = word["translation"]

    words = [w["word"] for w in words]
    row_words = {w: 0 for w in words}
    word_distances = [row_words for w in words]
    word_distances = pd.DataFrame(word_distances, index=words)
    word_distances = word_distances.apply(calculate_word_distance, axis=1)

    word_distances["translation"] = word_distances.apply(lambda x: translations[x.name], axis=1)
    for word in word_distances.columns:
        word_distances = word_distances.sort_values(word, ascending=False)
        if word != "translation" and word_distances[word].iloc[1] > 90 and len(word) > 2:

            translation = word_distances.iloc[0]["translation"].replace("/", "-")
            output_path = Path(f"DEBUG/word_distances/{word}-{translation}.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            word_distances[[word, "translation"]].to_csv(output_path)

    word_distances.to_csv("DEBUG/word_distances/_fuzzwy.csv")
