from articles.models import (
    Wikipedia,
    Wikipedia_sentence,
    Subtitle,
    Subtitle_sentence,
    Lyric,
    Lyric_sentence,
    Rss,
    Rss_sentence,
)


supported_languages = ["ar", "he"]
supported_sources = ["rss", "lyric", "subtitle", "wikipedia"]
language_name_to_code = {"arabic": "ar", "hebrew": "he"}


def check_language_supported(language: str):
    if language not in supported_languages:
        raise Exception(f"Language should be one of {supported_languages}")
    return True


def check_source_supported(source: str):
    if source not in supported_sources:
        raise Exception(f"Source should be one of {supported_sources}")
    return True


def chunks(list: list, size: int):
    size = max(1, size)
    return (list[i : i + size] for i in range(0, len(list), size))


def get_source_model(source_name: str):
    match source_name:
        case "rss":
            return Rss, Rss_sentence
        case "lyric":
            return Lyric, Lyric_sentence
        case "wikipedia":
            return Wikipedia, Wikipedia_sentence
        case "subtitle":
            return Subtitle, Subtitle_sentence
