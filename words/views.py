from .forms import WordsForm
from django.shortcuts import redirect, render
from words.models import Word, WordRating
from django.conf import settings
from django.db.models import Prefetch

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}
language_code_mapping = {"ar": "arabic", "he": "hebrew"}


def model_result_to_dict(model_result, key="text"):
    out_dict = {}
    for res in model_result:
        out_dict[res[key]] = res
    return out_dict


def get_flexions(word):
    flexions = word.flexion_counts
    if not flexions:
        flexions = {}

    flexions_sum = sum(list(flexions.values()))
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
            root = root.replace(" ", "-")
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
            rating = word.word_ratings_list[-1].rating
        except:
            rating = None

        word_to_show = {
            "word": word.text,
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


def word(request, language_code):
    language = language_code_mapping[language_code]

    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    if request.method == "GET":
        language = request.GET.get("language", language)
        word_text = request.GET.get("word", 0)

        queryset = WordRating.objects.filter(user=request.user)

        word = Word.objects.prefetch_related(
            Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        ).filter(
            language=language,
            text=word_text
        )
        word_to_show = build_words_to_show(word)[0]

    elif request.method == "POST":
        raise notImplementedError

    speech_voice = language_speech_mapping.get(language, "en")

    return render(
        request,
        "flashcards.html",
        {
            "words": [word_to_show],
            "words_to_show_dict": model_result_to_dict([word_to_show], "word"),
            "speech_voice": speech_voice,
            "url_parameters": {
                "language": language
            },
            "user_auth_token": request.user.auth_token,
            "user_username": request.user.username,
        },
    )


def flashcards(request, language_code):
    language = language_code_mapping[language_code]

    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    if request.method == "GET":
        lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
        upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

        queryset = WordRating.objects.filter(user=request.user)
        words = Word.objects.prefetch_related(
            Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        ).filter(
            language=language,
            rank__gt=lower_freq_cutoff,
            rank__lte=upper_freq_cutoff,
        )

        words_to_show = build_words_to_show(words)
        words_to_show = sorted(words_to_show, key=lambda d: d["frequency"], reverse=True)

        url_parameters = {
            "lower_freq_cutoff": lower_freq_cutoff,
            "upper_freq_cutoff": upper_freq_cutoff,
            "language_code": language_code,
        }
    elif request.method == "POST":
        words_to_show = []

        for key, value in request.POST.items():
            if key.startswith("select-word-"):
                words_to_show.append(value)

        queryset = WordRating.objects.filter(user=request.user)
        words = Word.objects.prefetch_related(
            Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
        ).filter(language=language, text__in=words_to_show)
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
            "user_word_ratings": build_user_word_ratings(request.user),
            "url_parameters": url_parameters,
            "user_auth_token": request.user.auth_token,
        },
    )

def index(request, language_code):
    language = language_code_mapping[language_code]

    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    sort_source = ""

    lower_freq_cutoff = int(request.GET.get("lower_freq_cutoff", 0))
    upper_freq_cutoff = int(request.GET.get("upper_freq_cutoff", 100))

    if (upper_freq_cutoff - lower_freq_cutoff > 500):
        request.GET._mutable = True
        request.GET["lower_freq_cutoff"] = lower_freq_cutoff
        request.GET["upper_freq_cutoff"] = lower_freq_cutoff + 100
        return index(request, language_code)
    
    queryset = WordRating.objects.filter(user=request.user)
    words = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
    ).filter(
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
        "language_code": language_code,
    }
    return render(
        request,
        "index.html",
        {
            "words": words_to_show,
            "words_to_show_dict": model_result_to_dict(words_to_show, "word"),
            "user_word_ratings": build_user_word_ratings(request.user),
            "url_parameters": url_parameters,
            "form": form,
            "user_auth_token": request.user.auth_token,
        },
    )


def index_default(request):
    return index(request, "he")


def build_user_word_ratings(user):
    words = []
    res = WordRating.objects.select_related().filter(user=user)
    for w in res:
        words.append({"word": w.word.text, "rating": w.rating})
    return words
