from .helpers import get_source_model, supported_sources, supported_language_codes
from words.models import Word, Flexion


def run(*args):
    for language in supported_language_codes:
        print("=====================================")
        print(f"Stats: {language}")

        print("Sources:")
        for source in supported_sources:
            source_model, source_sentences = get_source_model(source)
            print(f"{source}: {source_model.objects.filter(language=language).count()}")

            source_sentences_count = source_sentences.objects.filter(
                language=language
            ).count()
            source_sentences_unparsed_count = source_sentences.objects.filter(
                language=language, parsed_clean=None
            ).count()
            print(f"{source} sentences: {source_sentences_count}")
            print(
                f"{source} sentences unparsed: {source_sentences_unparsed_count} ({int(source_sentences_unparsed_count/source_sentences_count*100)}%)"
            )

        print("")
        print("Words:")
        word_count = Word.objects.filter(language=language).count()
        print("Count", word_count)
        for source in supported_sources:
            print(
                f"NULL count_{source}",
                Word.objects.filter(
                    language=language, **{f"count_{source}": None}
                ).count()
                / word_count
                * 100,
            )

        print("")
        print("Flexions:")
        flexion_count = Flexion.objects.filter(language=language).count()
        print("Count", flexion_count)
        if flexion_count == 0:
            continue
        for source in supported_sources:
            print(
                f"NULL count_{source}",
                Flexion.objects.filter(
                    language=language, **{f"count_{source}": None}
                ).count()
                / flexion_count
                * 100,
            )
