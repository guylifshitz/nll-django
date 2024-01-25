import pandas as pd
import requests
from io import StringIO
import string
import traceback
import re

prefixes = ["ה", "ב", "כ", "ל", "מ", "ש", "כש", "ו"]
pronouns = [
    "אני",
    "אתה",
    # "את",
    "הוא",
    "היא",
    "אנחנו",
    "אתם",
    "אתן",
    "הם",
    "הן",
]


def get_parts(text):
    text = text.replace('"', "'")
    localhost_yap = "http://localhost:8000/yap/heb/joint"
    data = '{{"text": "{}  "}}'.format(text).encode(
        "utf-8"
    )  # input string ends with two space characters
    headers = {"content-type": "application/json"}
    response = requests.get(url=localhost_yap, data=data, headers=headers)
    json_response = response.json()
    return json_response["md_lattice"]


def parse_titles(titles):
    parsed_titles_cleaned = []
    parsed_titles_lemma = []
    parsed_titles_segmented = []
    parsed_titles_prefixes = []
    parsed_titles_POSTAG = []
    parsed_titles_FEATS = []
    parsed_titles_roots = []
    parsed_titles_gloss_lemma = []
    parsed_titles_gloss_flexion = []

    for title_idx, title in enumerate(titles):
        print("-------")
        print(f"Title#{title_idx}: {title}")

        try:
            # Replace Gershayim
            title = re.sub(r'(?<=[\u0590-\u05FF])"(?=[\u0590-\u05FF])', "״", title)
            title = re.sub(r"(?<=[\u0590-\u05FF])\'\'(?=[\u0590-\u05FF])", "״", title)

            title = title.translate(
                str.maketrans({key: " {0} ".format(key) for key in string.punctuation})
            )

            title_cleaned = title.split(" ")
            title_cleaned = list(filter(lambda x: x != "", title_cleaned))

            parts = get_parts(" ".join(title_cleaned))
            header = [
                "FROM",
                "TO",
                "FORM",
                "LEMMA",
                "CPOSTTAG",
                "POSTAG",
                "FEATS",
                "TOKEN",
            ]
            parts = pd.read_csv(StringIO(parts), sep="\t", names=header)
            parts.to_csv("TESTparts.csv")
            title_segments = []
            title_lemmas = []
            title_prefixes = []
            title_POSTAG = []
            title_FEATS = []

            non_words = ["PREPOSITION", "CONJ", "DEF", "IN", "REL"]
            for token_idx, group in parts.groupby("TOKEN"):
                token_lemma = None
                token_POSTAG = None
                token_FEATS = None
                token_segments = []
                token_prefixes = []

                for idx, row in group.iterrows():
                    token_segments += [row["FORM"]]

                    # The parser converts the pronouns to הוא, we want to keep them as they are
                    if row["FORM"] in pronouns:
                        row["LEMMA"] = row["FORM"]

                    if row["POSTAG"] not in non_words:
                        if token_lemma:
                            try:
                                token_lemma = title_cleaned[token_idx - 1]
                            except:
                                token_lemma = "XXX"
                            print(f"-\nEXTRA LEMMA ({token_lemma})\n", group)
                            parts.to_csv(f"DEBUG/{row['LEMMA']}.csv")
                        token_lemma = row["LEMMA"]
                        token_POSTAG = row["POSTAG"]
                        token_FEATS = row["FEATS"]
                    else:
                        if row["LEMMA"] in prefixes:
                            token_prefixes.append(row["LEMMA"])
                        token_POSTAG = row["POSTAG"]
                if not token_lemma:
                    # token_lemma = "???"
                    try:
                        token_lemma = title_cleaned[token_idx - 1]
                    except:
                        token_lemma = "XXX"
                    print(f"-\nNO LEMMA ({token_lemma})\n", group)
                title_lemmas.append(token_lemma)
                title_POSTAG.append(token_POSTAG)
                title_FEATS.append(token_FEATS)
                title_segments.append("+".join(token_segments))
                title_prefixes.append(token_prefixes)

            if not (
                len(title_cleaned)
                == len(title_lemmas)
                == len(title_segments)
                == len(title_prefixes)
                == len(title_POSTAG)
                == len(title_FEATS)
            ):
                print("TITLE COMPONENTS ARE NOT ALL SAME SIZE")
                title_cleaned = None
                title_lemmas = None
                title_segments = None
                title_prefixes = None
                title_POSTAG = None
                title_FEATS = None
        except Exception:
            print("Skipping title due to an exception.")
            print(traceback.format_exc())
            title_cleaned = None
            title_lemmas = None
            title_segments = None
            title_prefixes = None
            title_POSTAG = None
            title_FEATS = None

        parsed_titles_cleaned.append(title_cleaned)
        parsed_titles_lemma.append(title_lemmas)
        parsed_titles_segmented.append(title_segments)
        parsed_titles_prefixes.append(title_prefixes)
        parsed_titles_POSTAG.append(title_POSTAG)
        parsed_titles_FEATS.append(title_FEATS)
        parsed_titles_roots.append(None)
        parsed_titles_gloss_lemma.append(None)
        parsed_titles_gloss_flexion.append(None)

    return (
        parsed_titles_cleaned,
        parsed_titles_lemma,
        parsed_titles_segmented,
        parsed_titles_prefixes,
        parsed_titles_POSTAG,
        parsed_titles_FEATS,
        parsed_titles_roots,
        parsed_titles_gloss_lemma,
        parsed_titles_gloss_flexion,
    )
