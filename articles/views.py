from .forms import ArticlesForm, ArticlesFormFromFile
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words, Flexions
import datetime
import traceback
import pandas as pd
from io import BytesIO
from collections import defaultdict

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}

default_end_date = datetime.datetime.now()
default_start_date = default_end_date - datetime.timedelta(days=7)
default_end_date = default_end_date.strftime("%d-%m-%Y")
default_start_date = default_start_date.strftime("%d-%m-%Y")


def model_result_to_dict(model_result):
    out_dict = {}
    for res in model_result:
        out_dict[res["_id"]] = res
    return out_dict


def get_verb_tenses(postag, features):
    if postag == "VB":
        number = ""
        if "num=S" in features:
            number = "s"
        elif "num=P" in features:
            number = "p"

        person = ""
        if "per=1" in features:
            person = "1"
        elif "per=2" in features:
            person = "2"
        elif "per=3" in features:
            person = "3"

        tense = ""
        if "tense=FUTURE" in features:
            tense = "futr"
        elif "tense=PAST" in features:
            tense = "past"
        elif "tense=IMPERATIVE" in features:
            tense = "impe"
        elif "tense=BEINONI" in features:
            tense = "bein"

        return tense + "-" + person + number
    return None


def get_word_known_categories_from_df(words, known_words_df):
    word_known_category = {}

    practice_words = known_words_df[known_words_df["TYPE"] == "PRACTICE"]["word"].values.tolist()
    known_words = known_words_df[known_words_df["TYPE"] == "KNOWN"]["word"].values.tolist()
    seen_words = known_words_df[known_words_df["TYPE"] == "SEEN"]["word"].values.tolist()

    for word in known_words:
        word_known_category[word] = "known"
    for word in practice_words:
        word_known_category[word] = "practice"
    for word in seen_words:
        word_known_category[word] = "seen"

    return word_known_category


def get_word_known_categories_from_cutoffs(words, known_cutoff, practice_cutoff, seen_cutoff):
    word_known_category = {}
    for word in words[0:known_cutoff]:
        word_known_category[word["_id"]] = "known"
    for word in words[known_cutoff:practice_cutoff]:
        word_known_category[word["_id"]] = "practice"
    for word in words[practice_cutoff:seen_cutoff]:
        word_known_category[word["_id"]] = "seen"
    return word_known_category


def build_article_words(article, words, word_known_categories, flexions):

    article_words = []
    for article_lemma_index, lemma_text in enumerate(article["title_parsed_lemma"]):

        ##########
        # LEMMA STUFF
        lemma_obj = words[lemma_text]
        lemma_diacritic = lemma_obj["word_diacritic"]
        if not lemma_diacritic:
            lemma_diacritic = lemma_text
        word_index = list(words.keys()).index(lemma_text)
        word_translation = lemma_obj["translation"].lower()

        lemma_known_status = word_known_categories.get(lemma_text, "unknown")

        #########
        # ARTICLE STUFF
        word_foreign_flexion = article["title_parsed_clean"][article_lemma_index]
        flexion_translation = flexions.get(word_foreign_flexion, {"translation_google": "NONE"})[
            "translation_google"
        ].lower()

        token_segmented = article["title_parsed_segmented"][article_lemma_index]

        token_POS = article["title_parsed_POSTAG"][article_lemma_index]

        # NNP = proper noun
        is_proper_noun = False
        if token_POS == "NNP":
            word_translation = f"##{word_foreign_flexion}##"
            flexion_translation = f"##{word_foreign_flexion}##"
            word_foreign_flexion = f"##{word_foreign_flexion}##"
            is_proper_noun = True

        # CD = cardinal digit?
        if token_POS == "CD":
            word_translation = word_foreign_flexion

        verb_tense = get_verb_tenses(token_POS, article["title_parsed_FEATS"][article_lemma_index])

        token_prefixes = article["title_parsed_prefixes"][article_lemma_index]
        token_prefixes = ("".join(token_prefixes) + "+") if token_prefixes else ""

        # CUSTOM TRANSLATIONS (currently verbs that are precomputed, later maybe user suggested words)
        translation_override = article["title_parsed_translation_override"][article_lemma_index]
        if translation_override:
            word_translation = translation_override

        word_components = {
            "word_foreign": word_foreign_flexion,
            "flexion_translation": flexion_translation,
            "lemma_foreign": lemma_text,
            "lemma_foreign_diacritic": lemma_diacritic,
            "lemma_foreign_index": word_index,
            "lemma_known": lemma_known_status == "known",
            "lemma_practice": lemma_known_status == "practice",
            "lemma_seen": lemma_known_status == "seen",
            "lemma_known_status": lemma_known_status,
            "word_translation": word_translation,
            "token_segmented": token_segmented,
            "verb_tense": verb_tense,
            "is_proper_noun": is_proper_noun,
            "token_prefixes": token_prefixes,
        }
        article_words.append(word_components)

    return article_words


def index(request):

    if request.method == "POST":
        form = ArticlesFormFromFile(request.POST, request.FILES)
        print("form.is_valid()", form.is_valid())
        print("form.errors", form.errors)
        if form.is_valid():
            data = request.FILES["file"].read()
            known_words_df = pd.read_csv(BytesIO(data))

            language = request.POST.get("language", "arabic")
            start_date_cutoff_raw = request.POST.get("start_date", default_start_date)
            start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%d-%m-%Y")
            end_date_cutoff_raw = request.POST.get("end_date", default_end_date)
            end_date_cutoff = datetime.datetime.strptime(end_date_cutoff_raw, "%d-%m-%Y")
            article_display_count = int(request.POST.get("count", 100))
            sort_by_word = request.POST.get("sort_by_word", "NOTESET") != "NOTESET"

    if request.method == "GET":
        language = request.GET.get("language", "arabic")
        known_cutoff = int(request.GET.get("known_cutoff", 50))
        practice_cutoff = int(request.GET.get("practice_cutoff", 50))
        seen_cutoff = int(request.GET.get("seen_cutoff", 50))
        start_date_cutoff_raw = request.GET.get("start_date", default_start_date)
        start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%d-%m-%Y")
        end_date_cutoff_raw = request.GET.get("end_date", default_end_date)
        end_date_cutoff = datetime.datetime.strptime(end_date_cutoff_raw, "%d-%m-%Y")
        article_display_count = int(request.GET.get("count", 100))
        sort_by_word = request.GET.get("sort_by_word", "NOTESET") != "NOTESET"

    articles = Rss_feeds.objects.filter(
        language=language,
        published_datetime__gte=start_date_cutoff,
        published_datetime__lte=end_date_cutoff,
        title_translation__ne=None,
    )
    articles = articles
    print(f"Got {len(articles)} articles")

    words = Words.objects.filter(language=language).order_by("-count")
    flexions = Flexions.objects.filter(language=language)
    flexions = model_result_to_dict(flexions)

    if request.method == "POST":
        word_known_categories = get_word_known_categories_from_df(words, known_words_df)
    else:
        word_known_categories = get_word_known_categories_from_cutoffs(
            words, known_cutoff, practice_cutoff, seen_cutoff
        )
    words = model_result_to_dict(words)
    print(f"Got {len(words)} words")

    articles_to_render = []
    article_sources = defaultdict(dict)

    for article in articles:
        try:
            article_to_render = {}
            article_to_render["title"] = article["title"]
            article_to_render["title_parsed_clean"] = article["title_parsed_clean"]
            article_to_render["feed_source"] = article["source"]
            article_to_render["feed_name"] = article["feed_name"]
            article_sources[article["source"]][article["feed_name"]] = 1

            article_to_render["published_datetime"] = article["published_datetime"]
            article_to_render["title_translation"] = article["title_translation"]
            article_to_render["link"] = article["link"]

            article_words = build_article_words(article, words, word_known_categories, flexions)
            article_to_render["words"] = article_words
            known_words_count = sum([aw["lemma_known"] for aw in article_words])
            practice_words_count = sum([aw["lemma_practice"] for aw in article_words])
            seen_words_count = sum([aw["lemma_seen"] for aw in article_words])

            article_to_render["known_words_count"] = known_words_count
            article_to_render["practice_words_count"] = practice_words_count
            article_to_render["seen_words_count"] = seen_words_count
            article_to_render["practice_words_ratio"] = practice_words_count / max(
                len(article_words), 1
            )
            article_to_render["known_practice_seen_words_ratio"] = (
                known_words_count + practice_words_count + seen_words_count
            ) / max(len(article_words), 1)

            if article_to_render["words"] and article_to_render["practice_words_count"] > 0:
                articles_to_render.append(article_to_render)
        except Exception as e:
            traceback.print_exc()

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["known_practice_seen_words_ratio"], reverse=True
    )

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["practice_words_ratio"], reverse=True
    )

    articles_to_render = sorted(
        articles_to_render,
        key=lambda d: len(d["words"])
        - (d["known_words_count"] + d["seen_words_count"] + d["practice_words_count"]),
        reverse=False,
    )

    # DEBUG
    # import debug
    # debug.count_article_words(articles_to_render, practice_cutoff)

    if sort_by_word:
        articles_to_render = sort_articles_by_word(articles_to_render)

    articles_to_render = articles_to_render[0:article_display_count]
    speech_voice = language_speech_mapping[language]

    if request.method == "GET":
        form = ArticlesForm(
            initial={
                "start_date": start_date_cutoff_raw,
                "end_date": end_date_cutoff_raw,
                "language": language,
                "known_cutoff": known_cutoff,
                "practice_cutoff": practice_cutoff,
                "seen_cutoff": seen_cutoff,
                "article_display_count": article_display_count,
                "sort_by_word": sort_by_word,
            }
        )

        url_parameters = {
            "known_cutoff": known_cutoff,
            "practice_cutoff": practice_cutoff,
            "seen_cutoff": seen_cutoff,
            "language": language,
        }
    else:
        form = None
        url_parameters = None

    return render(
        request,
        "articles.html",
        {
            "articles": articles_to_render,
            "speech_voice": speech_voice,
            "form": form,
            "url_parameters": url_parameters,
            "article_sources": article_sources.keys(),
        },
    )


def sort_articles_by_word(articles):
    articles_per_lemma = {}
    ret_articles = []
    for article in articles:
        for word in article["words"]:
            if word["lemma_practice"]:
                articles_per_lemma.setdefault(word["lemma_foreign"], []).append(article)

    while len(articles_per_lemma) > 0:
        for lemma in list(articles_per_lemma.keys()):
            print(len(articles_per_lemma[lemma]))
            art = articles_per_lemma[lemma].pop(0)
            if art not in ret_articles:
                art["title_translation"] = lemma + ":" + art["title_translation"]
                ret_articles.append(art)
            if len(articles_per_lemma[lemma]) == 0:
                del articles_per_lemma[lemma]
    return ret_articles


def configure(request):
    language = request.GET.get("language", "arabic")
    known_cutoff = int(request.GET.get("known_cutoff", 50))
    practice_cutoff = int(request.GET.get("practice_cutoff", 100))
    seen_cutoff = int(request.GET.get("seen_cutoff", practice_cutoff))
    start_date_cutoff = request.GET.get("start_date", default_start_date)
    end_date_cutoff = request.GET.get("end_date", default_end_date)
    article_display_count = int(request.GET.get("count", 100))
    sort_by_word = request.GET.get("sort_by_word", "False") == "False"

    form = ArticlesForm(
        initial={
            "start_date": start_date_cutoff,
            "end_date": end_date_cutoff,
            "language": language,
            "known_cutoff": known_cutoff,
            "practice_cutoff": practice_cutoff,
            "seen_cutoff": seen_cutoff,
            "article_display_count": article_display_count,
            "sort_by_word": sort_by_word,
        }
    )
    form_from_file = ArticlesFormFromFile(
        initial={
            "start_date": start_date_cutoff,
            "end_date": end_date_cutoff,
            "language": language,
            "article_display_count": article_display_count,
            "sort_by_word": sort_by_word,
        }
    )
    return render(request, "configure.html", {"form": form, "form2": form_from_file})
