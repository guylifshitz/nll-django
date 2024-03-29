from .forms import ArticlesForm, ArticlesFormFromPOST
from django.shortcuts import render
from articles.models import Rss_feed
from words.models import Word, Flexion, WordRating
import datetime
import traceback
from collections import defaultdict
import json
from django.db import connection
from django.db.models import Prefetch

language_speech_mapping = {"ar": "ar-SA", "he": "he"}
language_code_mapping = {"ar": "arabic", "he": "hebrew"}

default_end_date = datetime.datetime.now()
default_start_date = default_end_date - datetime.timedelta(days=7)
default_end_date = default_end_date.strftime("%Y-%m-%d")
default_start_date = default_start_date.strftime("%Y-%m-%d")


def model_result_to_dict(model_result):
    out_dict = {}
    for res in model_result:
        out_dict[res.text] = res
    return out_dict


def format_features(postag, features):
    if not features:
        return ""

    number = ""
    if "num=S" in features:
        number = "s"
    elif "num=P" in features:
        number = "p"

    gender = ""
    if "gen=M" in features:
        gender = "m"
    elif "gen=F" in features:
        gender = "f"

    person = ""
    if "per=1" in features:
        person = "1"
    elif "per=2" in features:
        person = "2"
    elif "per=3" in features:
        person = "3"

    tense = ""
    if "tense=FUTURE" in features:
        tense = "futr."
    elif "tense=PAST" in features:
        tense = "past."
    elif "tense=IMPERATIVE" in features:
        tense = "impe."
    elif "tense=BEINONI" in features:
        tense = "bein."

    return "".join([tense, person, gender, number])


def get_word_known_categories_from_df(words, known_words_df):

    practice_words = known_words_df[known_words_df["TYPE"] == "PRACTICE"]["word"].values.tolist()
    known_words = known_words_df[known_words_df["TYPE"] == "KNOWN"]["word"].values.tolist()
    seen_words = known_words_df[known_words_df["TYPE"] == "SEEN"]["word"].values.tolist()

    word_known_category = get_word_known_categories_from_lists(
        words, known_words, practice_words, seen_words
    )
    return word_known_category


def get_word_known_categories_from_lists(words, known_words, practice_words, seen_words):
    word_known_category = {}

    for word in known_words:
        word_known_category[word] = "known"
    for word in practice_words:
        word_known_category[word] = "practice"
    for word in seen_words:
        word_known_category[word] = "seen"

    return word_known_category


def get_word_known_categories_from_cutoffs(words, known_cutoff, practice_cutoff, seen_cutoff):
    word_known_category = {}
    for word in words:
        if word["rank"] <= known_cutoff:
            word_known_category[word["_id"]] = "known"
        elif known_cutoff < word["rank"] <= practice_cutoff:
            word_known_category[word["_id"]] = "practice"
        elif practice_cutoff < word["rank"] <= seen_cutoff:
            word_known_category[word["_id"]] = "seen"
    return word_known_category


def build_article_words(article, words, word_known_categories, flexions):

    article_words = []
    for article_lemma_index, lemma_text in enumerate(article.title_parsed_lemma):

        ##########
        # LEMMA STUFF
        lemma_diacritic = lemma_text
        word_rank = 0

        try:
            lemma_obj = words[lemma_text]
            lemma_diacritic = lemma_obj.word_diacritic
            word_rank = lemma_obj.rank
            word_translation = lemma_obj.translation
            if not word_translation:
                word_translation = "[[error]]"
            word_translation = word_translation.lower()
            lemma_root = get_root(lemma_obj)
        except Exception:
            word_rank = "-"
            word_translation = "[[error]]"
            lemma_root = "[[error]]"

        try:
            lemma_rating = lemma_obj.word_ratings_list[-1].rating
        except:
            lemma_rating = "-"

        lemma_known_status = word_known_categories.get(lemma_text, "unknown")

        if not lemma_diacritic:
            lemma_diacritic = lemma_text

        #########
        # ARTICLE STUFF
        word_foreign_flexion = article.title_parsed_clean[article_lemma_index]
        try:
            flexion_translation = flexions.get(word_foreign_flexion).translation_google
        except:
            flexion_translation = "[[error]]"
        if not flexion_translation:
            flexion_translation = flexions.get(word_foreign_flexion).translation_azure
        if not flexion_translation:
            flexion_translation = ""
        flexion_translation = flexion_translation.lower()

        token_segmented = article.title_parsed_segmented[article_lemma_index]

        token_POS = article.title_parsed_postag[article_lemma_index]

        # NNP = proper noun
        is_proper_noun = False
        if token_POS == "NNP" or "/PUNC" in token_POS or "/NAME" in token_POS:
            # word_translation = f"##{word_foreign_flexion}##"
            # flexion_translation = f"##{word_foreign_flexion}##"
            # word_foreign_flexion = f"##{word_foreign_flexion}##"
            is_proper_noun = True

        is_prep_pronoun = False
        if token_POS == "S_PRN":
            is_prep_pronoun = True

        # CD = cardinal digit?
        if token_POS == "CD":
            word_translation = word_foreign_flexion

        features = article.title_parsed_feats[article_lemma_index]
        features = format_features(token_POS, features)

        token_prefixes = article.title_parsed_prefixes[article_lemma_index]
        token_prefixes = ("".join(token_prefixes) + "+") if token_prefixes else ""

        # CUSTOM TRANSLATIONS (currently verbs that are precomputed, later maybe user suggested words)
        translation_override = article.title_parsed_translation_override[article_lemma_index]
        if translation_override:
            word_translation = translation_override

        word_components = {
            "word_foreign": word_foreign_flexion,
            "flexion_translation": flexion_translation,
            "lemma_foreign": lemma_text,
            "lemma_foreign_diacritic": lemma_diacritic,
            "lemma_foreign_index": word_rank,
            "lemma_root": lemma_root,
            "lemma_known": lemma_known_status == "known",
            "lemma_practice": lemma_known_status == "practice",
            "lemma_seen": lemma_known_status == "seen",
            "lemma_known_status": lemma_known_status,
            "lemma_rating": lemma_rating,
            "word_translation": word_translation,
            "token_segmented": token_segmented,
            # "verb_tense": verb_tense,
            "is_proper_noun": is_proper_noun,
            "is_prep_pronoun": is_prep_pronoun,
            "features": features,
            "token_prefixes": token_prefixes,
        }
        article_words.append(word_components)

    return article_words


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


def cleanup_source_name(source_name):
    # TODO split this up by language.
    source_name_mapping = {
        "ynet-hebrew": "ynet",
        "mako-hebrew": "mako",
        "haaretz-hebrew": "haaretz",
        "globes-hebrew": "globes",
        "bbc-arabic": "bbc-arabic",
        "cnn-arabic": "cnn-arabic",
        "aljazeera-arabic": "aljazeera-arabic",
    }
    return source_name_mapping[source_name]


def index(request, language_code):
    language = language_code_mapping[language_code]

    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    if request.method == "POST":
        form = ArticlesFormFromPOST(request.POST)

        practice_words = request.POST.get("practice_words")
        practice_words = json.loads(practice_words)

        known_words = request.POST.get("known_words")
        if known_words:
            known_words = json.loads(known_words)
        else:
            known_words = WordRating.objects.filter(user=request.user).all().values_list("word__text", flat=True)

        start_date_cutoff_raw = request.POST.get("start_date", default_start_date)
        start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%Y-%m-%d")
        end_date_cutoff_raw = request.POST.get("end_date", default_end_date)
        end_date_cutoff = datetime.datetime.strptime(end_date_cutoff_raw, "%Y-%m-%d")
        article_display_count = int(request.POST.get("article_display_count", 100))
        sort_by_word = request.POST.get("sort_by_word", "NOTESET") != "NOTESET"
        sort_by_practice_only = request.POST.get("sort_by_practice_only", "SET") != "NOTESET"

        # if form.is_valid():
        # print(form)
        # print("request.POST", request.POST)
        # data = request.
        # # known_words_df = pd.read_csv(BytesIO(data))
        # known_words_df = known_words_json
        # language = request.POST.get("language", "hebrew")
        # start_date_cutoff_raw = request.POST.get("start_date", default_start_date)
        # start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%d-%m-%Y")
        # end_date_cutoff_raw = request.POST.get("end_date", default_end_date)
        # end_date_cutoff = datetime.datetime.strptime(end_date_cutoff_raw, "%d-%m-%Y")
        # article_display_count = int(request.POST.get("article_display_count", 100))

    if request.method == "GET":
        known_cutoff = int(request.GET.get("known_cutoff", 50))
        practice_cutoff = int(request.GET.get("practice_cutoff", 50))
        seen_cutoff = int(request.GET.get("seen_cutoff", 50))
        start_date_cutoff_raw = request.GET.get("start_date", default_start_date)
        start_date_cutoff = datetime.datetime.strptime(start_date_cutoff_raw, "%d-%m-%Y")
        end_date_cutoff_raw = request.GET.get("end_date", default_end_date)
        end_date_cutoff = datetime.datetime.strptime(end_date_cutoff_raw, "%d-%m-%Y")
        article_display_count = int(request.GET.get("article_display_count", 100))
        sort_by_word = request.GET.get("sort_by_word", "NOTESET") != "NOTESET"

    if request.method == "POST":
        query_words = practice_words
        query_sort_words = list(practice_words)
        if sort_by_practice_only:
            query_sort_words.extend(known_words)
    else:
        query_words = Word.objects.filter(
            language=language,
            rank__gt=known_cutoff,
            rank__lte=practice_cutoff,
            # rank__gt=0,
            # rank__lte=seen_cutoff,
        ).order_by("-count")
        query_words = model_result_to_dict(query_words)
        query_words = list(query_words.keys())

    # sort_query_words = (
    #     Words.objects.filter(
    #         language=language,
    #         # rank__gt=known_cutoff,
    #         # rank__lte=practice_cutoff,
    #         rank__gt=0,
    #         rank__lte=seen_cutoff,
    #     )
    #     .order_by("-count")
    # )
    # sort_query_words = model_result_to_dict(sort_query_words)
    # sort_query_words = list(sort_query_words.keys())
    # print(start_date_cutoff)
    # print(end_date_cutoff)
    # test = Rss_feeds.objects.filter(
    #     language=language,
    #     published_datetime__gte=start_date_cutoff,
    #     published_datetime__lte=end_date_cutoff,
    #     # title_translation__ne=None,
    #     title_parsed_lemma={"$elemMatch": {"$in": query_words}},
    # )[0:100]
    # print("test")
    # print(test)
    # for t in test:
    #     print(t["title_parsed_clean"])
    # print("DONE test")

    # import pdb

    # pdb.set_trace()

    # cursor = Rss_feeds.objects.mongo_aggregate(
    #     [
    #         {
    #             "$match": {
    #                 "language": language,
    #                 "title_parsed_lemma": {"$elemMatch": {"$in": query_words}},
    #             }
    #         },
    #         {
    #             "$project": {
    #                 "title_parsed_lemma": "$title_parsed_lemma",
    #                 "title": "$title_parsed_lemma",
    #                 "found_lemmas": {
    #                     "$filter": {
    #                         "input": "$title_parsed_lemma",
    #                         "as": "thing",
    #                         "cond": {"$in": ["$$thing", query_sort_words]},
    #                     }
    #                 },
    #             }
    #         },
    #         {"$limit": 10},
    #     ]
    # )

    # for r in cursor:
    #     print(r)

    # result = Rss_feeds.objects.mongo_aggregate([])

    # filter(
    #         language=language,
    #         published_datetime__gte=start_date_cutoff,
    #         published_datetime__lte=end_date_cutoff,
    #         # title_translation__ne=None,
    #         title_parsed_lemma={"$elemMatch": {"$in": query_words}},
    #     # )
    article_ids = []
    known_words_words = list(known_words)
    with connection.cursor() as cursor:
        # query = """(SELECT id, ratio FROM 
        # (SELECT id, lemma_found_count::decimal / title_parsed_lemma_length::decimal AS ratio FROM
        # (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
        # array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS lemma_found_count
        # FROM articles_rss_feed WHERE published_datetime >= %s AND published_datetime <= %s AND language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY ratio desc limit %s);"""
        # cursor.execute(
        #     query, [query_words, start_date_cutoff, end_date_cutoff, language, article_display_count]
        # )

        query = """(SELECT id, ratio, lemma_found_count, known_found_count FROM 
        (SELECT id, lemma_found_count, known_found_count, lemma_found_count::decimal / title_parsed_lemma_length::decimal AS ratio FROM
        (SELECT id, array_length("title_parsed_lemma", 1) AS title_parsed_lemma_length, 
        array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS lemma_found_count,
        array_length(ARRAY( SELECT * FROM UNNEST( "title_parsed_lemma" ) WHERE UNNEST = ANY( array[%s])),1) AS known_found_count
        FROM articles_rss_feed WHERE published_datetime >= %s AND published_datetime <= %s AND language = %s) t1 ) t2 WHERE ratio NOTNULL ORDER BY lemma_found_count desc, known_found_count desc NULLS LAST limit %s);"""
        cursor.execute(
            query, [query_words, known_words_words, start_date_cutoff, end_date_cutoff, language, article_display_count]
        )
        rows = cursor.fetchall()

        article_ids = []
        for r in rows:
            print(r[0])
            article_ids.append(r[0])
        print("article_ids", article_ids)

        article_ids = article_ids[0:article_display_count+1]

    articles = Rss_feed.objects.filter(link__in=article_ids)

    print(f"Got {len(articles)} articles")

    lemmas = set()
    flexions = set()
    for article in articles:
        lemmas = lemmas | set(article.title_parsed_lemma)
        flexions = flexions | set(article.title_parsed_clean)

    queryset = WordRating.objects.filter(user=request.user)
    lemmas = Word.objects.prefetch_related(
        Prefetch("word_ratings", to_attr="word_ratings_list", queryset=queryset)
    ).filter(language=language, text__in=list(lemmas))

    if request.method == "POST":
        # word_known_categories = get_word_known_categories_from_df(lemmas, known_words_df)
        word_known_categories = get_word_known_categories_from_lists(
            lemmas, known_words, practice_words, []
        )
    else:
        word_known_categories = get_word_known_categories_from_cutoffs(
            lemmas, known_cutoff, practice_cutoff, seen_cutoff
        )

    lemmas = model_result_to_dict(lemmas)
    print(f"Got {len(lemmas)} lemmas")

    flexions = Flexion.objects.filter(language=language, text__in=list(flexions))
    flexions = model_result_to_dict(flexions)
    print(f"Got {len(flexions)} flexions")

    articles_to_render = []
    article_sources = defaultdict(dict)

    for article in articles:
        try:
            article_to_render = {}
            article_to_render["title"] = article.title
            article_to_render["title_parsed_clean"] = article.title_parsed_clean
            article_to_render["feed_source"] = cleanup_source_name(article.source)
            article_to_render["feed_names"] = article.feed_names
            for feed_name in article.feed_names:
                article_sources[cleanup_source_name(article.source)][feed_name] = 1

            article_to_render["published_datetime"] = article.published_datetime
            article_to_render["title_translation"] = article.title_translation
            article_to_render["link"] = article.link
            article_to_render["summary"] = article.summary

            article_words = build_article_words(article, lemmas, word_known_categories, flexions)
            article_to_render["words"] = article_words
            known_words_count = sum([aw["lemma_known"] for aw in article_words])
            practice_words_count = sum([aw["lemma_practice"] for aw in article_words])
            seen_words_count = sum([aw["lemma_seen"] for aw in article_words])
            unknown_words_count = sum(
                [
                    not (
                        aw["lemma_seen"]
                        or aw["lemma_known"]
                        or aw["lemma_practice"]
                        or aw["is_proper_noun"]
                    )
                    for aw in article_words
                ]
            )
            # proper_nouns_count = sum([aw["is_proper_noun"] for aw in article_words])
            article_to_render["is_about_sports"] = is_article_about_sports(article)

            article_to_render["known_words_count"] = known_words_count
            article_to_render["practice_words_count"] = practice_words_count
            article_to_render["seen_words_count"] = seen_words_count
            # article_to_render["proper_nouns_count"] = proper_nouns_count
            article_to_render["practice_words_ratio"] = int(
                practice_words_count / max(len(article_words), 1) * 100
            )
            article_to_render["known_practice_seen_words_ratio"] = int(
                (
                    unknown_words_count
                    # (
                    #     known_words_count
                    #     + practice_words_count
                    #     + seen_words_count
                    #     # + proper_nouns_count
                    # )
                    / max(len(article_words), 1)
                )
                * 100
            )

            if article_to_render["words"] and article_to_render["practice_words_count"] > 0:
                articles_to_render.append(article_to_render)
        except Exception:
            traceback.print_exc()

    articles_to_render = filter(lambda a: a["practice_words_count"] > 0, articles_to_render)

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["known_practice_seen_words_ratio"], reverse=False
    )

    # Remove sports
    articles_to_render = list(filter(lambda a: (not a["is_about_sports"]), articles_to_render))

    # if sort_by_practice_only:
    #     articles_to_render = sorted(
    #         articles_to_render, key=lambda d: d["practice_words_ratio"], reverse=True
    #     )

    # articles_to_render = sorted(
    #     articles_to_render, key=lambda d: d["practice_words_ratio"], reverse=True
    # )
    # articles_to_render = sorted(
    #     articles_to_render, key=lambda d: d["practice_words_count"], reverse=True
    # )

    # articles_to_render = sorted(
    #     articles_to_render,
    #     key=lambda d: len(d["words"])
    #     - (d["known_words_count"] + d["seen_words_count"] + d["practice_words_count"]),
    #     reverse=False,
    # )

    # DEBUG
    # import debug
    # debug.count_article_words(articles_to_render, practice_cutoff)

    if sort_by_word:
        articles_to_render = sort_articles_by_word(articles_to_render)

    articles_to_render = articles_to_render[0:article_display_count]
    speech_voice = language_speech_mapping[language_code]

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
            "language_code": language_code,
        }
    else:
        form = None
        url_parameters = {
            "language_code": language_code,
        }

    return render(
        request,
        "articles.html",
        {
            "articles": articles_to_render,
            "speech_voice": speech_voice,
            "form": form,
            "url_parameters": url_parameters,
            "article_sources": dict(article_sources),
            "user_auth_token": request.user.auth_token,
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
            art = articles_per_lemma[lemma].pop(0)
            if art not in ret_articles:
                art["title_translation"] = lemma + ":" + art["title_translation"]
                ret_articles.append(art)
            if len(articles_per_lemma[lemma]) == 0:
                del articles_per_lemma[lemma]
    return ret_articles


def configure(request, language_code):
    language = language_code_mapping[language_code]
    known_cutoff = int(request.GET.get("known_cutoff", 50))
    practice_cutoff = int(request.GET.get("practice_cutoff", 100))
    seen_cutoff = int(request.GET.get("seen_cutoff", practice_cutoff))
    start_date_cutoff = request.GET.get("start_date", default_start_date)
    end_date_cutoff = request.GET.get("end_date", default_end_date)
    article_display_count = int(request.GET.get("article_display_count", 100))
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
    return render(request, "configure.html", {"form": form})


def is_article_about_sports(article):
    sports_words = ["sport", "soccer", "football", "basketball"]
    link_contains_sport_word = any(word in article.link.lower() for word in sports_words)

    feedname_contains_sport_word = False
    for feed_name in article.feed_names:
        feedname_contains_sport_word = feedname_contains_sport_word or any(
            word in feed_name.lower() for word in sports_words
        )

    return link_contains_sport_word or feedname_contains_sport_word


def sort_articles_by_word(articles):
    articles_per_lemma = {}
    ret_articles = []
    for article in articles:
        for word in article["words"]:
            if word["lemma_practice"]:
                articles_per_lemma.setdefault(word["lemma_foreign"], []).append(article)

    while len(articles_per_lemma) > 0:
        for lemma in list(articles_per_lemma.keys()):
            art = articles_per_lemma[lemma].pop(0)
            if art not in ret_articles:
                art["title_translation"] = lemma + ":" + art["title_translation"]
                ret_articles.append(art)
            if len(articles_per_lemma[lemma]) == 0:
                del articles_per_lemma[lemma]
    return ret_articles
