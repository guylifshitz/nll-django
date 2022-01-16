from django.http import HttpResponse
from django.shortcuts import render
from articles.models import Rss_feeds
from words.models import Words
import datetime


def index(request):
    word_count_cutoff = int(request.GET.get("word_count_cutoff", 10))
    start_date_cutoff = request.GET.get("start_date", "01-01-1900")
    start_date_cutoff = datetime.datetime.strptime(start_date_cutoff, "%d-%m-%Y")

    articles = Rss_feeds.objects.filter(
        published_datetime__gte=start_date_cutoff, title_translation__ne=None
    )

    articles_to_render = []
    for article in articles:
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
            lemma = Words.objects(_id=lemma)[0]

            mix_word = lemma["translation"].lower()
            mix_word_translation = article["title_parsed_clean"][index]
            mix_word_lemma = lemma["_id"]

            mix_word_segmented = lemma["translation"].lower()
            mix_word_segmented_translation = article["title_parsed_segmented"][index]

            if lemma["count"] > word_count_cutoff:
                mix_word = article["title_parsed_clean"][index]
                mix_word_translation = lemma["translation"].lower()

                mix_word_segmented = article["title_parsed_segmented"][index]
                if lemma["_id"] not in mix_word_segmented:
                    mix_word_segmented = mix_word_segmented + f"({lemma['_id']})"

                mix_word_segmented_translation = lemma["translation"].lower()

                known_words_count = known_words_count + 1

            word_components = {
                "word": article["title_parsed_clean"][index],
                "lemma": lemma["_id"],
                "mix": mix_word,
                "mix_word_translation": mix_word_translation,
                "mix_word_lemma": mix_word_lemma,
                "mix_segmented": mix_word_segmented,
                "mix_word_translation_segmented": mix_word_segmented_translation,
                "translation": lemma["translation"].lower(),
            }
            words.append(word_components)

        article_to_render["words"] = words
        article_to_render["known_words_count"] = known_words_count
        article_to_render["known_words_ratio"] = known_words_count / max(len(words), 1)

        articles_to_render.append(article_to_render)

    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["published_datetime"], reverse=True
    )
    articles_to_render = sorted(
        articles_to_render, key=lambda d: d["known_words_ratio"], reverse=True
    )
    articles_to_render = articles_to_render[0:100]
    return render(request, "articles.html", {"articles": articles_to_render})
