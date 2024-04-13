import pandas as pd
import requests
from io import StringIO
import string
import traceback
import re
from random import randint
from articles.models import Sentence

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

# ABVERB 	The word כ before numerals
# AT 	Accusative marker את which appears as a separate word in written Hebrew
# BN 	BN – participle (בינוני)
# BNN 	Participle (בינוני) in construct state form
# CC 	Conjunction
# CD 	Numeral
# CDT 	Numeral in construct state
# CONJ 	Coordinating conjunction ו
# COP 	Copula
# COP_TOINFINITIVE 	The infinitive form of the verb היה used as a copula
# DEF 	A special tag assigned to the definiteness marker ה, which appears with nouns, adjectives and numerals
# DT 	Used in the treebank only for the determiner כל with a pronominal suffix
# DTT 	Determiner
# DUMMY_AT 	Accusative marker אתwhen used with a pronominal suffix
# EX 	existential marker יש or אין
# IN 	Preposition
# INTJ 	Interjection
# JJ 	Adjective
# JJT 	Adjective in construct state
# MD 	Modal predicates
# NN 	Noun
# NN_S_PP 	Noun with a pronominal suffix
# NNP 	Proper noun
# NNT 	Construct state noun
# P 	Prefix written as a separate word (אי, בלתי,אנטי etc.)
# POS 	Possessive preposition של and accusative marker את with a pronominal suffix
# PREPOSITION 	Inseparable preposition
# PRP 	Personal pronoun
# QW 	Question word
# S_PRN 	Personal pronoun attached to a preposition as a pronominal suffix
# TEMP 	Subordinating conjunction introducing time clauses
# VB 	Verb
# VB_TOINFINITIVE 	A verb in its infinitive form
# yyCLN 	Colon
# yyCM 	Comma
# yyDASH 	Hyphen or dash
# yyDOT 	Period
# yyELPS 	Ellipsis (...)
# yyEXCL 	Exclamation point
# yyLRB 	Left parenthesis
# yyQM 	Question mark
# yyQUOT 	Quotation mark
# yyRRB 	Right parenthesis
# yySCLN 	Semicolon

pos_to_simple_pos = {
    "ABVERB": "_",
    "AT": "et",
    "BN": "verb",
    "BNN": "verb",
    "CC": "conjunction",
    "CD": "numeral",
    "CDT": "numeral",
    "CONJ": "conjunction",
    "COP": "_",
    "COP_TOINFINITIVE": "verb",
    "DEF": "definiteness marker",
    "DT": "_",
    "DTT": "determiner",
    "DUMMY_AT": "et",
    "EX": "existential marker",
    "IN": "preposition",
    "INTJ": "interjection",
    "JJ": "adjective",
    "JJT": "adjective",
    "MD": "modal predicates",
    "NN": "noun",
    "NN_S_PP": "noun",
    "NNP": "proper noun",
    "NNT": "noun",
    "P": "_",
    "POS": "_",
    "PREPOSITION": "preposition",
    "PRP": "personal pronoun",
    "QW": "question word",
    "S_PRN": "_",
    "TEMP": "_",
    "VB": "verb",
    "VB_TOINFINITIVE": "verb",
    "yyCLN": "punctuation",
    "yyCM": "punctuation",
    "yyDASH": "punctuation",
    "yyDOT": "punctuation",
    "yyELPS": "punctuation",
    "yyEXCL": "punctuation",
    "yyLRB": "punctuation",
    "yyQM": "punctuation",
    "yyQUOT": "punctuation",
    "yyRRB": "punctuation",
    "yySCLN": "punctuation",
}


def parse_sentences(sentences: list[Sentence]):
    for idx, sentence in enumerate(sentences):
        parsed_line = parse_line(sentence.text)

        all_same_length = all(
            [len(parsed_line[i]) == len(parsed_line[0]) for i in range(6)]
        )
        if not all_same_length:
            print("Problem with parsing title. Skipping...")
            continue

        sentence.parsed_clean = parsed_line[0]
        sentence.parsed_lemma = parsed_line[1]
        sentence.parsed_segmented = parsed_line[2]
        sentence.parsed_prefixes = parsed_line[3]
        sentence.parsed_pos = parsed_line[4]
        # sentence.parsed_pos_simple = [pos_to_simple_pos[pos] for pos in parsed_line[4]]
        sentence.parsed_features = parsed_line[5]
        sentence.parsed_roots = None
        sentence.parsed_gloss_lemma = None
        sentence.parsed_gloss_flexion = None


def parse_line(sentence_text: str):
    try:
        # Replace Gershayim
        sentence_text = re.sub(
            r'(?<=[\u0590-\u05FF])"(?=[\u0590-\u05FF])', "״", sentence_text
        )
        sentence_text = re.sub(
            r"(?<=[\u0590-\u05FF])\'\'(?=[\u0590-\u05FF])", "״", sentence_text
        )

        sentence_text = sentence_text.translate(
            str.maketrans({key: " {0} ".format(key) for key in string.punctuation})
        )

        # TODO use a good tokenizer
        title_cleaned = sentence_text.split(" ")
        title_cleaned = list(filter(lambda x: x != "", title_cleaned))
        print(sentence_text)
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
            f.write(f"{sentence_text}\n")
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


def parse_sentence_api(text: str):
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
