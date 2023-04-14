from numpy import sort, source
from .forms import WordsForm
from django.shortcuts import redirect, render
from words.models import Words, WordRatings
from django.conf import settings


language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}


def model_result_to_dict(model_result, key="_id"):
    out_dict = {}
    for res in model_result:
        out_dict[res[key]] = res
    return out_dict


def get_flexions(word):
    flexions = word.flexion_counts
    if not flexions:
        flexions = {}

    flexions_sum = sum(list(flexions.values()))
    print(flexions_sum)
    flexions = {k: v for k, v in sorted(flexions.items(), key=lambda item: item[1], reverse=True)}
    flexions = {k: max(int(v / flexions_sum * 100), 1) for k, v in flexions.items()}
    flexions = {k: flexions[k] for k in list(flexions)[:10]}

    if not flexions:
        flexions = ""
    return flexions


def get_root(word):
    root = word.root

    if not root:
        if word.user_roots:
            hyphens = ["־", "–", "-"]
            root = word.user_roots[-1]
            root = root.replace(" ", "")
            for h in hyphens:
                root = root.replace(h, " - ")
    if not root:
        root = ""

    return root


def get_translation(word):
    translation = word.translation
    if word.user_translations:
        translation = word.user_translations[-1]
    if not translation:
        translation = ""

    return translation


def build_words_to_show(words, sort_source=None):
    words_to_show = []
    for idx, word in enumerate(words):
        try:
            rating = word.wordratings_set.last().rating
        except:
            rating = None

        word_to_show = {
            "word": word._id,
            "word_diacritic": word.word_diacritic,
            "translation": get_translation(word),
            "root": get_root(word),
            "flexions": get_flexions(word),
            "frequency": word.count,
            "language": word.language,
            "index": word.rank,
            "rating": rating,
            "user_translations": word.user_translations or [],
            "user_roots": word.user_roots or [],
        }

        if sort_source == "open_subtitles":
            word_to_show["index"] = word.rank_open_subtitles
            word_to_show["frequency"] = word.count_open_subtitles

        if not word.word_diacritic:
            word_to_show["word_diacritic"] = word_to_show["word"]
        words_to_show.append(word_to_show)
    return words_to_show


def flashcards(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    
    if request.method == "GET":
        language = request.GET.get("language", "hebrew")
        lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
        upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

        words = Words.objects.filter(
            language=language,
            rank__gt=lower_freq_cutoff,
            rank__lte=upper_freq_cutoff,
        ).order_by("rank_open_subtitles")
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

        words = Words.objects.filter(language=language, _id__in=words_to_show)
        words_to_show = build_words_to_show(words)
        url_parameters = {
            "lower_freq_cutoff": 0,
            "upper_freq_cutoff": 0,
            "language": language,
        }

    speech_voice = language_speech_mapping.get(language, "en")

    return render(
        request,
        "flashcards.html",
        {
            "words": words_to_show,
            "words_to_show_dict": model_result_to_dict(words_to_show, "word"),
            "speech_voice": speech_voice,
            "url_parameters": url_parameters,
            "user_auth_token": request.user.auth_token
        },
    )


def index(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    sort_source = ""

    language = request.GET.get("language", "hebrew")
    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    words = None
    if sort_source == "open_subtitles":
        words = Words.objects.filter(
            language=language,
            rank_open_subtitles__gt=lower_freq_cutoff,
            rank_open_subtitles__lte=upper_freq_cutoff,
        ).order_by("rank_open_subtitles")
    else:
        words = Words.objects.filter(
            language=language,
            rank__gt=lower_freq_cutoff,
            rank__lte=upper_freq_cutoff,
        ).order_by("rank")

    words_to_show = build_words_to_show(words, sort_source=sort_source)

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
        "index.html",
        {
            "words": words_to_show,
            "words_to_show_dict": model_result_to_dict(words_to_show, "word"),
            "url_parameters": url_parameters,
            "form": form,
            "user_auth_token": request.user.auth_token
        },
    )

