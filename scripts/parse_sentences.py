from articles.models import Wikipedia, Wikipedia_sentence, Sentence
from pprint import pprint
from django.conf import settings
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)
import pandas as pd
import scripts.language_parsers.arabic.parser_camel as arabic_parser
import scripts.language_parsers.hebrew.parser2 as hebrew_parser

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
    sentences = get_unparsed_sentences(language, sentence_model, limit=fetch_limit)

    for sentence_chunk in chunks(sentences, chunk_size):
        print(f"Processing {len(sentence_chunk)} sentences")
        parse_sentences(sentence_chunk, language)


def get_unparsed_sentences(language: str, sentence_model: Sentence, limit: int = None):
    unparsed_sentences = sentence_model.objects.filter(
        language=language, parsed_lemma__isnull=True
    ).all()
    if limit:
        unparsed_sentences = unparsed_sentences[:limit]

    print(f"Found {len(unparsed_sentences)} unparsed sentences")
    return unparsed_sentences


def parse_sentences(sentences: list[Sentence], language: str):
    if language == "ar":
        parser = arabic_parser
    elif language == "he":
        parser = hebrew_parser
    else:
        raise Exception("Langauge parser not implemented for {language}")

    parser.parse_sentences(sentences)

    print("Saving...")
    for sentence in sentences:
        sentence.save()
