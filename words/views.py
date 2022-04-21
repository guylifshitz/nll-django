from .forms import WordsForm
from django.shortcuts import render
from words.models import Words
from django.conf import settings


language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}


def build_words_to_show(words):
    words_to_show = []
    for idx, word in enumerate(words):
        word_to_show = {
            "word": word["_id"],
            "word_diacritic": word["word_diacritic"],
            "translation": word["translation"],
            "root": word["root"],
            "frequency": word["count"],
            "language": word["language"],
            "index": word["rank"],
            "user_translations": word["user_translations"],
            "user_roots": word["user_roots"],
        }

        if not word["root"]:
            word_to_show["root"] = ""

        if not word["word_diacritic"]:
            word_to_show["word_diacritic"] = word_to_show["word"]
        words_to_show.append(word_to_show)
    return words_to_show


def flashcards(request):
    if request.method == "GET":
        language = request.GET.get("language", "hebrew")
        lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
        upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

        words = Words.objects.filter(
            language=language,
            rank__gt=lower_freq_cutoff,
            rank__lte=upper_freq_cutoff,
        ).order_by("rank")
        words_to_show = build_words_to_show(words)
        words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)

        url_parameters = {
            "lower_freq_cutoff": lower_freq_cutoff,
            "upper_freq_cutoff": upper_freq_cutoff,
            "language": language,
        }
    elif request.method == "POST":
        language = request.POST.get("language", "hebrew")

        words_to_show = []

        for key, value in request.POST.items():
            if key.startswith("select-word-"):
                words_to_show.append(value)

        words = Words.objects.filter(language=language, _id={"$in": words_to_show})
        words_to_show = build_words_to_show(words)
        url_parameters = {
            "lower_freq_cutoff": 0,
            "upper_freq_cutoff": 0,
            "language": language,
        }

    speech_voice = language_speech_mapping.get(language, "en")

    return render(
        request,
        "flashcards_new.html",
        # "flashcards.html",
        {"words": words_to_show, "speech_voice": speech_voice, "url_parameters": url_parameters},
    )


def index(request):
    language = request.GET.get("language", "hebrew")
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    words = Words.objects.filter(
        language=language,
        rank__gt=lower_freq_cutoff,
        rank__lte=upper_freq_cutoff,
    ).order_by("rank")
    words_to_show = build_words_to_show(words)

    # DEBUG
    # import debug
    # debug.calculate_word_distances(words_to_show)

    form = WordsForm(
        initial={
            "language": language,
            "lower_freq_cutoff": lower_freq_cutoff,
            "upper_freq_cutoff": upper_freq_cutoff,
        }
    )
    url_parameters = {
        "lower_freq_cutoff": lower_freq_cutoff,
        "upper_freq_cutoff": upper_freq_cutoff,
        "language": language,
    }
    return render(
        request,
        "index_new.html",
        {"words": words_to_show, "url_parameters": url_parameters, "form": form},
    )
