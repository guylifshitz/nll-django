from django.db.models import Func, F, Count
from articles.models import Sentence
from words.models import Flexion, Word
import pandas as pd

from pprint import pprint
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)

chunk_size = 1000


def run(*args):
    if len(args) != 2:
        raise Exception("2 arguments expected")
    language = args[0]
    source_name = args[1]
    check_language_supported(language)
    check_source_supported(source_name)

    print(f"Processing {language}/{source_name}")

    print("Finding flexions per lemma")
    source_model, sentence_model = get_source_model(source_name)
    lemma_flexion_df = find_flexions_per_lemma(language, sentence_model)
    print("Update counts")
    update_flexion_count(lemma_flexion_df, language, source_name)


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


def update_flexion_count(
    lemma_flexion_df: pd.DataFrame, language: str, source_name: str
):
    count_column = f"count_{source_name}"

    for lemma_text, group in lemma_flexion_df.groupby("lemma"):
        lemma = Word.objects.get(text=lemma_text, language=language)
        counts = group["flexion"].value_counts()
        for flexion_text, count in counts.items():
            Flexion.objects.filter(
                text=flexion_text, lemma=lemma, language=language
            ).update(**{count_column: count})
