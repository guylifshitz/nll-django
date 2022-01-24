from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
from mongoengine import Q
from django.conf import settings

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}


def get_words_to_show(language):
    words = Words.objects(language=language).order_by("-count")

    words_to_show = []
    for idx, word in enumerate(words):
        word_to_show = {
            "word": word["_id"],
            "word_diacritic": word["word_diacritic"],
            "translation": word["translation"],
            "frequency": word["count"],
            "language": word["language"],
            "index": idx,
        }
        if not word["word_diacritic"]:
            word_to_show["word_diacritic"] = word_to_show["word"]
        words_to_show.append(word_to_show)
    return words_to_show


def flashcards(request):
    language = request.GET.get("language", "arabic")
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 10))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 20))

    words_to_show = get_words_to_show(language)
    words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)

    if settings.ENVIRONMENT == "local":
        import pandas as pd

        pd.DataFrame(words_to_show).to_csv("words.csv")

    words_to_show = words_to_show[lower_freq_cutoff:upper_freq_cutoff]
    print(f"Last word frequency: {words_to_show[-1]['frequency']}")

    speech_voice = language_speech_mapping[language]

    return render(
        request, "flashcards.html", {"words": words_to_show, "speech_voice": speech_voice}
    )


def index(request):
    language = request.GET.get("language", "arabic")
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 10))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 20))

    words_to_show = get_words_to_show(language)
    words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)
    words_to_show = words_to_show[lower_freq_cutoff:upper_freq_cutoff]
    print("words_to_show")
    print(words_to_show)
    print(f"Last word frequency: {words_to_show[-1]['frequency']}")
    return render(request, "index.html", {"words": words_to_show})
