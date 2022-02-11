from .forms import ArticlesForm
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
import datetime
import traceback

language_speech_mapping = {"arabic": "ar-SA", "hebrew": "he"}


def model_result_to_dict(model_result):
    out_dict = {}
    for res in model_result:
        out_dict[res["_id"]] = res
    return out_dict


def count_article_words(articles, cutoff):
    import pandas as pd
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt

    words = []
    for article in articles:
        for word in article["words"]:
            if word["lemma_foreign_index"] < cutoff:
                words.append(word["lemma_foreign"])
    from collections import Counter

    print(Counter(words))

    # get per day
    aa = []
    for article in articles:
        a = {}
        a["published_datetime"] = article["published_datetime"]
        for word in article["words"]:
            if word["lemma_foreign_index"] < cutoff:
                a[word["lemma_foreign"]] = 1
        aa.append(a)

    df = pd.DataFrame(aa)
    df2 = df.groupby("published_datetime").count()
    df2.sort_values("published_datetime").to_csv("debug/per_date_word_counts.csv")

    for word in df2.columns:
        plt.clf()
        plot = df2[word].plot()
        fig = plot.get_figure()
        plt.title(word[::-1])
        fig.savefig(f"debug/charts/{word}.png")  


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


def build_article_words(article, words, word_known_count_cutoff, word_practice_count_cutoff):

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
        lemma_known = word_index <= word_known_count_cutoff
        lemma_practice = word_known_count_cutoff < word_index <= word_practice_count_cutoff
        if lemma_practice:
            lemma_known_status = "practice"
        elif lemma_known:
            lemma_known_status = "known"
        else:
            lemma_known_status = "unknown"

        #########
        # ARTICLE STUFF
        word_foreign_flexion = article["title_parsed_clean"][article_lemma_index]

        token_segmented = article["title_parsed_segmented"][article_lemma_index]

        token_POS = article["title_parsed_POSTAG"][article_lemma_index]
        if token_POS == "NNP":
            word_translation = f"##{word_foreign_flexion}##"

        verb_tense = get_verb_tenses(token_POS, article["title_parsed_FEATS"][article_lemma_index])

        token_prefixes = article["title_parsed_prefixes"][article_lemma_index]
        token_prefixes = ("".join(token_prefixes) + "+") if token_prefixes else ""

        # CUSTOM TRANSLATIONS (currently verbs that are precomputed, later maybe user suggested words)
        translation_override = article["title_parsed_translation_override"][article_lemma_index]
        if translation_override:
            word_translation = translation_override

        if token_POS == "CD":
            word_translation = word_foreign_flexion

        word_components = {
            "word_foreign": word_foreign_flexion,
            "lemma_foreign": lemma_text,
            "lemma_foreign_diacritic": lemma_diacritic,
            "lemma_foreign_index": word_index,
            "lemma_known": lemma_known,
            "lemma_practice": lemma_practice,
            "lemma_known_status": lemma_known_status,
            "word_translation": word_translation,
            "token_segmented": token_segmented,
            "verb_tense": verb_tense,
            "token_prefixes": token_prefixes,
        }
        article_words.append(word_components)

    return article_words


def index(request):
    language = request.GET.get("language", "arabic")
    known_cutoff = int(request.GET.get("known_cutoff", 50))
    practice_cutoff = int(request.GET.get("practice_cutoff", 50))
    start_date_cutoff_raw = request.GET.get("start_date", "01-01-1900")
    start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%d-%m-%Y")
    end_date_cutoff_raw = request.GET.get("end_date", "31-12-9999")
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
    words = model_result_to_dict(words)

    print(f"Got {len(words)} words")

    articles_to_render = []
    for article in articles:
        try:
            article_to_render = {}
            article_to_render["title"] = article["title"]
            article_to_render["title_parsed_clean"] = article["title_parsed_clean"]
            article_to_render["source"] = article["source"]
            article_to_render["feed_name"] = article["feed_name"]
            article_to_render["published_datetime"] = article["published_datetime"]
            article_to_render["title_translation"] = article["title_translation"]
            article_to_render["link"] = article["link"]

            article_words = build_article_words(article, words, known_cutoff, practice_cutoff)
            article_to_render["words"] = article_words
            known_words_count = sum([aw["lemma_known"] for aw in article_words])
            practice_words_count = sum([aw["lemma_practice"] for aw in article_words])

            article_to_render["known_words_count"] = known_words_count
            article_to_render["practice_words_count"] = practice_words_count
            article_to_render["practice_words_ratio"] = practice_words_count / max(
                len(article_words), 1
            )

            articles_to_render.append(article_to_render)
        except Exception as e:
            traceback.print_exc()

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["practice_words_ratio"], reverse=True
    )

    # DEBUG
    # count_article_words(articles_to_render, practice_cutoff)

    if sort_by_word:
        articles_to_render = sort_articles_by_word(articles_to_render)

    articles_to_render = articles_to_render[0:article_display_count]
    speech_voice = language_speech_mapping[language]

    form = ArticlesForm(
        initial={
            "start_date": start_date_cutoff_raw,
            "language": language,
            "known_cutoff": known_cutoff,
            "practice_cutoff": practice_cutoff,
            "article_display_count": article_display_count,
            "sort_by_word": sort_by_word,
        }
    )

    url_parameters = {
        "known_cutoff": known_cutoff,
        "practice_cutoff": practice_cutoff,
        "language": language,
    }

    return render(
        request,
        "articles.html",
        {
            "articles": articles_to_render,
            "speech_voice": speech_voice,
            "form": form,
            "url_parameters": url_parameters,
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
    start_date_cutoff = request.GET.get("start_date", "01-01-2022")
    article_display_count = int(request.GET.get("count", 100))
    sort_by_word = request.GET.get("sort_by_word", "False") == "False"

    form = ArticlesForm(
        initial={
            "start_date": start_date_cutoff,
            "language": language,
            "known_cutoff": known_cutoff,
            "practice_cutoff": practice_cutoff,
            "article_display_count": article_display_count,
            "sort_by_word": sort_by_word,
        }
    )
    return render(request, "configure.html", {"form": form})
