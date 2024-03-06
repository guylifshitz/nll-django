import psycopg2
from words.models import Word

from .helpers import (
    language_name_to_code,
)
import pandas as pd


def run(*args):
    existing_words_df = load_existing_words()
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
            raise f"More than one word found: {word_text} ({language}), found {len(res)} matches"
        res = res.first()

        print(f"Update {word_text}:{translation} ({language}) ")
        res.translation = translation

        res.save()
