import psycopg2
from words.models import Flexion

from .helpers import (
    language_name_to_code,
)
import pandas as pd


def run(*args):
    old_flexions_df = load_old_flexions()
    parse_flexions(old_flexions_df)


def load_old_flexions():
    connection = psycopg2.connect(
        "dbname='nll_production_copy_2024_01_22' user='guy' host='localhost'"
    )

    flexions_df = pd.read_sql("SELECT * FROM words_flexion", connection)
    return flexions_df


def parse_flexions(old_flexions_df):
    for index, row in old_flexions_df.iterrows():
        flexion_text = row["text"]
        translation_google = row["translation_google"]
        translation_azure = row["translation_azure"]
        language = row["language"]
        language_code = language_name_to_code[language]

        res = Flexion.objects.filter(text=flexion_text, language=language_code)
        if len(res) == 0:
            print(f"Flexion not found: {flexion_text} ({language})")
            continue
        if len(res) > 1:
            raise f"More than one flexion found: {flexion_text} ({language}), found {len(res)} matches"
        res = res.first()

        print(
            f"Update {flexion_text}:{translation_google}:{translation_azure}:({language})"
        )
        res.translation_google = translation_google
        res.translation_azure = translation_azure

        res.save()
