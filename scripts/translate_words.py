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

    source_model, sentence_model = get_source_model(source_name)
    print("source_model", source_model)

    words = get_words(source_name, language)
    process_words(words, language, translation_service)


def get_words(source_name: str, language: str):
    rank_column = f"rank_{source_name}"
    words = Word.objects.filter(
        language=language, **{f"{rank_column}__lte": rank_threshold}
    )
    print("words", words.count())
    return words


def process_words(words: list[Word], language: str, translation_service: str):
    for words_chunk in chunks(words, chunk_size):
        print(f"Processing {len(words_chunk)} words")
        word_texts = [word.text for word in words_chunk]
        if translation_service == "google":
            translated_texts = translate_texts_google(word_texts, language, "en")
            for word, translated_text in zip(words_chunk, translated_texts):
                word.translation_google = translated_text
                word.save()
        elif translation_service == "azure":
            translated_texts = translate_texts_azure(word_texts, language, "en")
            for word, translated_text in zip(words_chunk, translated_texts):
                word.translation_azure = translated_text
                word.save()
