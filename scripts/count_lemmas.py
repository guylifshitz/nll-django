from django.db.models import Func, F, Count
from articles.models import Sentence
from words.models import Word

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

    source_model, sentence_model = get_source_model(source_name)
    lemma_counts = count_lemmas(language, sentence_model)
    lemma_counts = calculate_lemma_ranks(lemma_counts)
    for lemma_chunk in chunks(lemma_counts, chunk_size):
        print(f"Processing {len(lemma_chunk)} lemmas")
        update_lemma_count(lemma_chunk, language, source_name)


def count_lemmas(language: str, sentence_model: Sentence) -> list[str]:
    lemma_counts = (
        sentence_model.objects.filter(language=language)
        .annotate(parsed_lemma2=Func(F("parsed_lemma"), function="unnest"))
        .values("parsed_lemma2")
        .annotate(count=Count("id"))
        .values_list("parsed_lemma2", "count")
    )
    return lemma_counts


def calculate_lemma_ranks(lemma_counts):
    lemma_counts = sorted(lemma_counts, key=lambda x: x[1], reverse=True)
    return [lemma_counts[i] + (i + 1,) for i in range(len(lemma_counts))]


def update_lemma_count(lemma_counts: list[str], language: str, source_name: str):
    count_column = f"count_{source_name}"
    rank_column = f"rank_{source_name}"
    for lemma_text, count, rank in lemma_counts:
        if lemma_text is None:
            continue
        Word.objects.filter(text=lemma_text, language=language).update(
            **{count_column: count, rank_column: rank}
        )

    return
