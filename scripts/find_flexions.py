from django.db.models import Func, F
from articles.models import Sentence
from words.models import Flexion

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
    flexions = get_all_flexions(language, sentence_model)

    for flexion_chunk in chunks(flexions, chunk_size):
        print(f"Processing {len(flexion_chunk)} flexions")
        insert_flexions(flexion_chunk, language)


def get_all_flexions(language: str, sentence_model: Sentence) -> list[str]:
    return (
        sentence_model.objects.annotate(
            flexions=Func(F("parsed_clean"), function="unnest")
        )
        .values_list("flexions", flat=True)
        .distinct()
    )


def insert_flexions(flexion_texts: list[str], language: str):
    print("Insert flexions")
    flexion_texts = filter(lambda x: x is not None, flexion_texts)
    flexion_objects = [
        Flexion(text=flexion_text, language=language) for flexion_text in flexion_texts
    ]

    Flexion.objects.bulk_create(flexion_objects, ignore_conflicts=True)
