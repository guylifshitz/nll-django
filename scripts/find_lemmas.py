from django.db.models import Func, F
from articles.models import Sentence
from words.models import Word

from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)

fetch_limit = 100000000
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

    print("Getting lemmas")
    lemmas = get_all_lemmas(language, sentence_model)

    for lemma_chunk in chunks(lemmas, chunk_size):
        print(f"Processing {len(lemma_chunk)} lemmas")
        insert_lemmas(lemma_chunk, language)


def get_all_lemmas(language: str, sentence_model: Sentence) -> list[str]:
    return (
        sentence_model.objects.annotate(
            lemmas=Func(F("parsed_lemma"), function="unnest")
        )
        .values_list("lemmas", flat=True)
        .distinct()
    )


def insert_lemmas(lemma_texts: list[str], language: str):
    print("Insert lemmas")
    lemma_texts = filter(lambda x: x is not None, lemma_texts)
    lemma_objects = [
        Word(text=lemma_text, language=language) for lemma_text in lemma_texts
    ]

    Word.objects.bulk_create(lemma_objects, ignore_conflicts=True)
