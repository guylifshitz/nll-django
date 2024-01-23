from words.models import Word
from articles.models import Wikipedia, Wikipedia_sentence, Sentence
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
    translate_texts_azure,
    translate_texts_google,
)

process_limit = 10
chunk_size = 1000


def run(*args):
    print(args)
    if len(args) != 3:
        raise Exception("3 arguments expected")
    language = args[0]
    source_name = args[1]
    translation_service = args[2]
    check_language_supported(language)
    if source_name != "rss":
        raise Exception(
            "Only rss source supported, otherwise it is too many sentences."
        )

    assert translation_service in ["google", "azure"]

    source_model, sentence_model = get_source_model(source_name)

    sentences = get_sentences(
        sentence_model, process_limit, translation_service, language
    )
    print("sentences", sentences.count())
    process_sentences(sentences, language, translation_service)


def get_sentences(
    sentence_model: Sentence,
    process_limit: int,
    translation_service: str,
    language: str,
):
    translation_column = f"translation_{translation_service}"
    sentences = sentence_model.objects.filter(
        language=language, **{f"{translation_column}__isnull": True}
    )[0:process_limit]
    print("sentences", sentences.count())
    return sentences


def process_sentences(
    sentences: list[Sentence],
    language: str,
    translation_service: str,
):
    for sentence_chunk in chunks(sentences, chunk_size):
        print(f"Processing {len(sentence_chunk)} sentences")
        sentence_texts = [sentence.text for sentence in sentence_chunk]
        if translation_service == "google":
            translated_texts = translate_texts_google(sentence_texts, language, "en")
            for sentence, translated_text in zip(sentence_chunk, translated_texts):
                sentence.translation_google = translated_text
                sentence.save()
        elif translation_service == "azure":
            translated_texts = translate_texts_azure(sentence_texts, language, "en")
            for sentence, translated_text in zip(sentence_chunk, translated_texts):
                sentence.translation_azure = translated_text
                sentence.save()
