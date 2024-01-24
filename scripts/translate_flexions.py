from words.models import Flexion
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
    translate_texts_azure,
    translate_texts_google,
)

rank_threshold = 10
chunk_size = 1000


def run(*args):
    print(args)
    if len(args) != 3:
        raise Exception("3 arguments expected")
    language = args[0]
    source_name = args[1]
    translation_service = args[2]
    check_language_supported(language)
    check_source_supported(source_name)
    assert translation_service in ["google", "azure"]

    print("translation_service", translation_service)
    source_model, sentence_model = get_source_model(source_name)
    print("source_model", source_model)

    print("Getting flexions")
    flexions = get_flexions(source_name, translation_service, language)
    print(f"Processing {len(flexions)} flexions")
    process_flexions(flexions, language, translation_service)


def get_flexions(
    source_name: str, translation_service: str, language: str
) -> list[Flexion]:
    count_column = f"count_{source_name}"
    translation_column = f"translation_{translation_service}"

    flexions = (
        Flexion.objects.filter(language=language)
        .exclude(**{f"{count_column}__isnull": True})
        .order_by(f"-{count_column}", "text")[:rank_threshold]
    )
    flexions = [
        flexion for flexion in flexions if getattr(flexion, translation_column) == None
    ]
    return flexions


def process_flexions(flexions: list[Flexion], language: str, translation_service: str):
    for flexions_chunk in chunks(flexions, chunk_size):
        print(f"Processing {len(flexions_chunk)} flexions")
        flexion_texts = [flexion.text for flexion in flexions_chunk]
        if translation_service == "google":
            translated_texts = translate_texts_google(flexion_texts, language, "en")
            for flexion, translated_text in zip(flexions_chunk, translated_texts):
                flexion.translation_google = translated_text
                flexion.save()
        elif translation_service == "azure":
            translated_texts = translate_texts_azure(flexion_texts, language, "en")
            for flexion, translated_text in zip(flexions_chunk, translated_texts):
                flexion.translation_azure = translated_text
                flexion.save()
