from django.db.models import Func, F
from articles.models import Sentence
from words.models import Flexion, Word
import pandas as pd

from pprint import pprint
from django.conf import settings
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)

fetch_limit = 100
chunk_size = 1000


def run(*args):
    if len(args) != 2:
        raise Exception("2 arguments expected")
    language = args[0]
    source_name = args[1]
    print("language", language)
    check_language_supported(language)
    check_source_supported(source_name)

    source_model, sentence_model = get_source_model(source_name)
    print("source_model", source_model)

    print("Getting flexions")
    lemma_flexion_df = find_flexions_per_lemma(language, sentence_model)
    insert_flexions(lemma_flexion_df, language)


# TODO harmonize with the code on count flexions
def find_flexions_per_lemma(language: str, sentence_model: Sentence) -> list[str]:
    queryset = (
        sentence_model.objects.filter(language=language)
        .filter(parsed_lemma__isnull=False)
        .annotate(parsed_flexion2=Func(F("parsed_clean"), function="unnest"))
        .annotate(parsed_lemma2=Func(F("parsed_lemma"), function="unnest"))
        .values_list("parsed_lemma2", "parsed_flexion2")
    )
    lemma_flexion_df = pd.DataFrame(queryset, columns=["lemma", "flexion"])
    return lemma_flexion_df


def insert_flexions(lemma_flexion_df: pd.DataFrame, language: str):
    print("Insert flexions")

    for lemma_text, group in lemma_flexion_df.groupby("lemma"):
        lemma = Word.objects.get(text=lemma_text, language=language)
        flexion_objects = [
            Flexion(text=flexion_text, lemma=lemma, language=language)
            for flexion_text in group["flexion"].unique()
        ]
        Flexion.objects.bulk_create(flexion_objects, ignore_conflicts=True)
