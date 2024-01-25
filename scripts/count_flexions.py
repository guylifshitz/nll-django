from django.db.models import Func, F, Count
from articles.models import Sentence
from words.models import Flexion

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

    print("Counting flexions")
    source_model, sentence_model = get_source_model(source_name)
    flexion_counts = count_flexions(language, sentence_model)
    print(f"Got {len(flexion_counts)} flexions")
    for flexion_chunk in chunks(flexion_counts, chunk_size):
        print(f"Processing {len(flexion_chunk)} flexions")
        update_flexion_count(flexion_chunk, language, source_name)


def count_flexions(language: str, sentence_model: Sentence) -> list[str]:
    flexion_counts = (
        sentence_model.objects.filter(language=language)
        .annotate(parsed_flexion2=Func(F("parsed_clean"), function="unnest"))
        .values("parsed_flexion2")
        .annotate(count=Count("id"))
        .values_list("parsed_flexion2", "count")
    )
    return flexion_counts


def update_flexion_count(flexion_counts: list[str], language: str, source_name: str):
    count_column = f"count_{source_name}"
    for flexion_text, count in flexion_counts:
        if flexion_text is None:
            continue
        Flexion.objects.filter(text=flexion_text, language=language).update(
            **{count_column: count}
        )

    return
