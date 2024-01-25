import pandas as pd
import requests
from io import StringIO
import string
import traceback
import re
from random import randint

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


def parse_sentence_api(text):
    text = text.replace('"', "'")
    localhost_yap = "http://localhost:8000/yap/heb/joint"
    data = '{{"text": "{}  "}}'.format(text).encode(
        "utf-8"
    )  # input string ends with two space characters
    headers = {"content-type": "application/json"}
    response = requests.get(url=localhost_yap, data=data, headers=headers)
    json_response = response.json()
    return json_response["md_lattice"]


def flatten(matrix):
    return [item for row in matrix for item in row]


def parse_sentences(sentences):
    parsed_lines = [parse_line(sentence) for sentence in sentences]

    sentences_cleaned = [x[0] for x in parsed_lines]
    sentences_lemma = [x[1] for x in parsed_lines]
    sentences_segmented = [x[2] for x in parsed_lines]
    sentences_prefixes = [x[3] for x in parsed_lines]
    sentences_POSTAG = [x[4] for x in parsed_lines]
    sentences_FEATS = [x[5] for x in parsed_lines]
    sentences_roots = [[] for x in parsed_lines]
    sentences_gloss_lemma = [[] for x in parsed_lines]
    sentences_gloss_flexion = [[] for x in parsed_lines]

    return (
        sentences_cleaned,
        sentences_lemma,
        sentences_segmented,
        sentences_prefixes,
        sentences_POSTAG,
        sentences_FEATS,
        sentences_roots,
        sentences_gloss_lemma,
        sentences_gloss_flexion,
    )


def parse_line(title_line):
    try:
        # Replace Gershayim
        title_line = re.sub(
            r'(?<=[\u0590-\u05FF])"(?=[\u0590-\u05FF])', "״", title_line
        )
        title_line = re.sub(
            r"(?<=[\u0590-\u05FF])\'\'(?=[\u0590-\u05FF])", "״", title_line
        )

        title_line = title_line.translate(
            str.maketrans({key: " {0} ".format(key) for key in string.punctuation})
        )

        # TODO use a good tokenizer
        title_cleaned = title_line.split(" ")
        title_cleaned = list(filter(lambda x: x != "", title_cleaned))
        print(title_line)
        parts = parse_sentence_api(" ".join(title_cleaned))
        header = ["FROM", "TO", "FORM", "LEMMA", "CPOSTTAG", "POSTAG", "FEATS", "TOKEN"]
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
                        print(title_cleaned)
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
                # print(f"-\nNO LEMMA ({token_lemma})\n", group)
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
            parts.to_csv(f"DEBUG/ERROR1:{randint(1,10000)}.csv")
            title_cleaned = ["BAD TITLE2"]
            title_lemmas = ["BAD TITLE2 "]
            title_segments = []
            title_prefixes = []
            title_POSTAG = []
            title_FEATS = []
    except Exception:
        with open(f"DEBUG/ERROR2:{randint(1,1000)}.txt", "a") as f:
            f.write(f"{title_line}\n")
        print("Skipping title due to an exception.")
        print(traceback.format_exc())
        title_cleaned = ["BAD TITLE1"]
        title_lemmas = ["BAD TITLE1"]
        title_segments = []
        title_prefixes = []
        title_POSTAG = []
        title_FEATS = []

    return (
        title_cleaned,
        title_lemmas,
        title_segments,
        title_prefixes,
        title_POSTAG,
        title_FEATS,
    )
