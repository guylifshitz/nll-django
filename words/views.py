from .forms import WordsForm
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
from mongoengine import Q
from django.conf import settings

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}


def calculate_word_distance(row):
    from fuzzywuzzy import fuzz
    import pandas as pd

    idx = row.name
    dffs = []
    col_names = []
    for col in row.iteritems():
        col = col[0]
        col_names.append(col)
        dif = fuzz.partial_ratio(idx, col)
        dffs.append(dif)
    return pd.Series(dffs, index=col_names)


def calculate_word_distances(words):
    import pandas as pd

    translations = {}
    for word in words:
        translations[word["word"]] = word["translation"]

    words = [w["word"] for w in words]
    row_words = {w: 0 for w in words}
    word_distances = [row_words for w in words]
    word_distances = pd.DataFrame(word_distances, index=words)
    word_distances = word_distances.apply(calculate_word_distance, axis=1)

    word_distances["translation"] = word_distances.apply(lambda x: translations[x.name], axis=1)
    for col in word_distances.columns:
        word_distances = word_distances.sort_values(col, ascending=False)
        if col != "translation" and word_distances[col].iloc[1] > 90 and len(col) > 2:
            word_distances[[col, "translation"]].to_csv(
                f"DEBUG/distances/{col}-{word_distances.iloc[0]['translation'].replace('/','-')}.csv"
            )

    word_distances.to_csv("DEBUG/fuzzwy.csv")


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
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    words_to_show = get_words_to_show(language)
    words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)

    if settings.ENVIRONMENT == "local":
        import pandas as pd

        pd.DataFrame(words_to_show).to_csv("words.csv")

    words_to_show = words_to_show[lower_freq_cutoff : upper_freq_cutoff + 1]

    speech_voice = language_speech_mapping.get(language, "en")

    url_parameters = {
        "lower_freq_cutoff": lower_freq_cutoff,
        "upper_freq_cutoff": upper_freq_cutoff,
        "language": language,
    }
    return render(
        request,
        "flashcards.html",
        {"words": words_to_show, "speech_voice": speech_voice, "url_parameters": url_parameters},
    )


def index(request):
    language = request.GET.get("language", "arabic")

    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    url_parameters = {
        "lower_freq_cutoff": lower_freq_cutoff,
        "upper_freq_cutoff": upper_freq_cutoff,
        "language": language,
    }

    words_to_show = get_words_to_show(language)
    words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)
    words_to_show = words_to_show[lower_freq_cutoff : upper_freq_cutoff + 1]

    # DEBUG
    # calculate_word_distances(words_to_show)

    form = WordsForm(
        initial={
            "language": language,
            "lower_freq_cutoff": lower_freq_cutoff,
            "upper_freq_cutoff": upper_freq_cutoff,
        }
    )

    return render(
        request,
        "index.html",
        {"words": words_to_show, "url_parameters": url_parameters, "form": form},
    )


def configure(request):
    language = request.GET.get("language", "arabic")
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 50))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    form = WordsForm(
        initial={
            "language": language,
            "lower_freq_cutoff": lower_freq_cutoff,
            "upper_freq_cutoff": upper_freq_cutoff,
        }
    )
    return render(request, "words_configure.html", {"form": form})
