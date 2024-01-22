from django.db.models import Func, F, Count
import psycopg2
from articles.models import Wikipedia, Wikipedia_sentence, Sentence
from words.models import Word

from pprint import pprint
from django.conf import settings
from .helpers import (
    language_name_to_code,
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)
import pandas as pd
import scripts.language_parsers.arabic.parser_camel as arabic_parser
import scripts.language_parsers.hebrew.parser2 as hebrew_parser


def run(*args):
    existing_words_df = load_existing_words().head(100)
    parse_words(existing_words_df)


def load_existing_words():
    connection = psycopg2.connect(
        "dbname='nll_production_copy_2024_01_22' user='guy' host='localhost'"
    )

    words_df = pd.read_sql("SELECT * FROM words_word", connection)
    return words_df


def parse_words(existing_words_df):
    for index, row in existing_words_df.iterrows():
        word_text = row["text"]
        translation = row["translation"]
        language = row["language"]
        language_code = language_name_to_code[language]

        res = Word.objects.filter(text=word_text, language=language_code)
        if len(res) == 0:
            print(f"Word not found: {word_text} ({language})")
            continue
        if len(res) > 1:
            raise "More than one word found: {word_text} ({language}), found {len(res)} matches"
        res = res.first()

        print(f"Update {word_text}:{translation} ({language}) ")
        res.translation = translation

        res.save()
