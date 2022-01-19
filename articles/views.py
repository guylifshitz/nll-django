from django.http import HttpResponse
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
import datetime
import traceback

def index(request):

    language = request.GET.get("language", "arabic")
    word_count_cutoff = int(request.GET.get("word_count_cutoff", 10))
    start_date_cutoff = request.GET.get("start_date", "01-01-1900")
    start_date_cutoff = datetime.datetime.strptime(start_date_cutoff, "%d-%m-%Y")

    articles = Rss_feeds.objects.filter(
        language=language, published_datetime__gte=start_date_cutoff, title_translation__ne=None
    )
    print("Got articles")

    words = Words.objects.filter()
    words_dict = {}
    for word in words:
        words_dict[word["_id"]] = word
    print("Got words")

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

            words = []
            known_words_count = 0
            for index, lemma in enumerate(article["title_parsed_lemma"]):
                lemma = words_dict[lemma]
                word_translation = lemma["translation"].lower()

                word_foreign = "foreign"
                mix_word = article["title_parsed_clean"][index]
                mix_word_translation = lemma["translation"].lower()
                mix_word_lemma = lemma["_id"]
                mix_word_segmented = article["title_parsed_segmented"][index]

                if lemma["_id"] not in mix_word_segmented:
                    mix_word_segmented = mix_word_segmented + f" ({lemma['_id']})"

                if lemma["count"] < word_count_cutoff:
                    word_foreign = "native"
                    mix_word = lemma["translation"].lower()
                    mix_word_translation = article["title_parsed_clean"][index]

                    mix_word_tooltip_1 = mix_word_translation
                    mix_word_tooltip_2 = mix_word_segmented

                else:
                    mix_word_tooltip_1 = mix_word_segmented
                    mix_word_tooltip_2 = mix_word_translation
                    known_words_count = known_words_count + 1

                word_components = {
                    "word": article["title_parsed_clean"][index],
                    "lemma": lemma["_id"],
                    "mix_word": mix_word,
                    "mix_word_translation": mix_word_translation,
                    "mix_word_lemma": mix_word_lemma,
                    "mix_word_tooltip_1": mix_word_tooltip_1,
                    "mix_word_tooltip_2": mix_word_tooltip_2,
                    "mix_segmented": mix_word_segmented,
                    "translation": word_translation,
                    "word_foreign": word_foreign,
                }
                words.append(word_components)

            article_to_render["words"] = words
            article_to_render["known_words_count"] = known_words_count
            article_to_render["known_words_ratio"] = known_words_count / max(len(words), 1)

            articles_to_render.append(article_to_render)
        except Exception as e:
            traceback.print_exc()

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )
    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["known_words_ratio"], reverse=True
    )
    articles_to_render = articles_to_render[0:100]
    return render(request, "articles.html", {"articles": articles_to_render})
