import django

django.setup()

from functools import partial
from pprint import pprint
from .helpers import (
    check_language_supported,
    check_source_supported,
    chunks,
    get_source_model,
)
import scripts.language_parsers.arabic.parser_camel as arabic_parser
import scripts.language_parsers.hebrew.parser2 as hebrew_parser
from multiprocessing import Pool

from articles.models import Sentence

fetch_limit = 100000000
chunk_size = 1000
pool_count = 8


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

    sentence_chunks = chunks(sentences, chunk_size)
    if pool_count == 1:
        for sentence_chunk in sentence_chunks:
            parse_sentences(sentence_chunk, language)
    else:
        with Pool(processes=pool_count) as pool:
            pool.map(partial(parse_sentences, language=language), sentence_chunks)


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
